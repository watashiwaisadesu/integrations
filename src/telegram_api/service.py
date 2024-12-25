import asyncio
import logging
import httpx
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.telegram_models import TelegramMessageLog
from src.db.repositories.external_service_app_repositories import get_app_external_service_base_url
from src.db.repositories.telegram_app_repositories import (
    get_current_app
)
from src.db.repositories.telegram_user_repositories import (
    add_or_update_telegram_user,
    get_user_by_phone, get_user_by_username,
)
from src.external_service.service import create_bot_request
from src.utils.errors_handler import InternalServerError, TelegramMessageHandlingError

logger = logging.getLogger(__name__)

async def request_code_service(phone_number: str, db: AsyncSession):
    """
    Request a login code for the given phone number using the current Telegram App credentials.
    Store the phone_code_hash and initial session in TelegramUser for later completion.
    """
    try:
        app = await get_current_app(db=db)
        api_id = app.api_id
        api_hash = app.api_hash

        session = StringSession()
        client = TelegramClient(session, api_id, api_hash)

        await client.connect()
        result = await client.send_code_request(phone_number)

        # Store the phone_code_hash AND the current session in the DB
        session_string = client.session.save()
        await add_or_update_telegram_user(
            phone_number=phone_number,
            db=db,
            app_id=app.id,
            phone_code_hash=result.phone_code_hash,
            session=session_string
        )

        logger.info(f"Code requested successfully for {phone_number}")
        return {"phone_code_hash": result.phone_code_hash}

    except Exception as e:
        # Log and re-raise as an internal error or define a custom one if desired
        logger.error(f"Error in request_code_service for {phone_number}: {e}")
        raise InternalServerError(f"Failed to request Telegram code for {phone_number}") from e


async def submit_code_service(phone_number: str, code: str, db: AsyncSession):
    """
    Submit the verification code received on the phone number and finalize login.
    """
    try:
        user = await get_user_by_phone(phone_number, db)
        if user is None or not user.phone_code_hash or not user.session:
            logger.warning(f"No phone_code_hash or session for phone {phone_number}. Possibly code not requested yet.")
            # Keep using ValueError to signal a 4xx error in the route
            raise ValueError("Phone number not found or code not requested. Request code first.")

        app = await get_current_app(db=db)
        api_id = app.api_id
        api_hash = app.api_hash

        temp_session = StringSession(user.session)
        client = TelegramClient(temp_session, api_id, api_hash)
        await client.connect()

        await client.sign_in(phone_number, code, phone_code_hash=user.phone_code_hash)
        session_string = client.session.save()

        me = await client.get_me()
        my_user_id = me.id if me else None
        username = me.username if me else None

        external_service_base_url = await get_app_external_service_base_url(db)
        bot_url = await create_bot_request(username, external_service_base_url, True)

        await add_or_update_telegram_user(
            phone_number=phone_number,
            db=db,
            session=session_string,
            username=username,
            user_id=str(my_user_id),
            phone_code_hash=None,
            bot_url=bot_url,
        )

        logger.info(f"User {phone_number} logged in successfully with username={username}.")
        asyncio.create_task(start_listening_service(client, phone_number, db))

        return {"session": session_string}

    except ValueError:
        # Let the route handle ValueError with a 4xx
        raise
    except Exception as e:
        logger.error(f"Unhandled error in submit_code_service for {phone_number}: {e}")
        raise InternalServerError("Failed to log in via Telegram.") from e


async def start_listening_service(client: TelegramClient, phone_number: str, db: AsyncSession):
    """
    Start the event handler for new messages and run until disconnected.
    """
    init_event_handlers_service(client, db)
    try:
        await client.run_until_disconnected()
    except asyncio.CancelledError:
        logger.info(f"Stopped listening for {phone_number}")


def init_event_handlers_service(client: TelegramClient, db: AsyncSession):
    """
    Initialize all event handlers for the client.
    """
    @client.on(events.NewMessage(incoming=True))
    async def handle_new_message(event):
        await handle_new_message_service(event, client, db)


async def handle_new_message_service(event, client, db: AsyncSession):
    """
    Handle incoming private messages:
    - Log them to DB
    - Create a response and send it back
    """
    try:
        if event.is_private:
            logger.debug(f"New private message event: {event}")
            me = await client.get_me()
            username = me.username if me else "unknown_username"
            sender = event.sender_id
            input_text = event.raw_text

            user = await get_user_by_username(username, db)
            if not user:
                logger.warning(f"No DB user record found for Telegram username={username}")

            # Save the message in the database
            log_entry = TelegramMessageLog(sender=str(sender), input_text=input_text)
            db.add(log_entry)
            await db.commit()

            logger.info(f"Message received from {sender}: {input_text}")

            # Forward to external service
            response_text = await forward_message_to_service(user.bot_url, input_text)

            # Fallback if no valid response
            if not response_text:
                logger.warning(f"No valid response received for input: {input_text}")
                response_text = "No response provided"

            # Update DB with the output
            log_entry.output_text = response_text
            db.add(log_entry)
            await db.commit()

            # Reply to the user in Telegram
            await event.reply(response_text)

    except Exception as e:
        logger.error(f"Error handling message from {event.sender_id}: {e}")
        # If you want a 500 in API routes triggered by a webhook, raise a custom TelegramMessageHandlingError.
        # If this code is purely background (not in a FastAPI route), you can log or re-raise as you wish.
        raise TelegramMessageHandlingError("Error in handle_new_message_service") from e


async def forward_message_to_service(bot_url: str, input_text: str):
    """
    Sends the user's message to the external service and retrieves the response.
    Returns a fallback string if the service fails or an unexpected error occurs,
    preserving your existing logic (don't break the flow).
    """
    payload = {
        "platform": "telegram",
        "message_text": input_text
    }
    headers = {"Content-Type": "application/json"}

    limits = httpx.Limits(max_connections=200, max_keepalive_connections=100)
    timeout = httpx.Timeout(10.0, connect=5.0, read=5.0, write=5.0)

    async with httpx.AsyncClient(limits=limits, timeout=timeout) as client:
        retries = 3
        delay = 1

        for attempt in range(retries):
            try:
                response = await client.post(bot_url, json=payload, headers=headers)

                logger.debug(f"Attempt {attempt + 1}: status={response.status_code}, text={response.text}")

                # If no text in response, treat as error
                if not response.text:
                    logger.error(f"Empty response from {bot_url}")
                    return "No response provided"

                # Attempt to parse JSON
                try:
                    result = response.json()
                    logger.info(f"Received response from external service: {result}")
                    return result.get("reply", "No reply provided")
                except ValueError as json_err:
                    logger.error(f"Invalid JSON from {bot_url}: {json_err}")
                    logger.error(f"Raw response content: {response.text}")
                    return "Invalid response format"

            except httpx.HTTPStatusError as http_err:
                logger.error(
                    f"HTTP error from {bot_url} on attempt {attempt + 1}: "
                    f"{http_err.response.status_code} - {http_err.response.text}"
                )
                if attempt < retries - 1:
                    await asyncio.sleep(delay * (2 ** attempt))
                else:
                    return f"Error {http_err.response.status_code}: Service issue."

            except httpx.RequestError as req_err:
                logger.error(f"Request error contacting {bot_url} on attempt {attempt + 1}: {req_err}")
                if attempt < retries - 1:
                    await asyncio.sleep(delay * (2 ** attempt))
                else:
                    return "Service is unavailable. Please try again later."

            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(delay * (2 ** attempt))
                else:
                    return "Unexpected error occurred."

        # If we exhaust all retries:
        return "Failed after multiple retries."
