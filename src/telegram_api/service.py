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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def request_code_service(phone_number: str, db: AsyncSession):
    """
    Request a login code for the given phone number using the current Telegram App credentials.
    Store the phone_code_hash and initial session in TelegramUser for later completion.
    """
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
        session=session_string  # store the session used for code request
    )

    return {"phone_code_hash": result.phone_code_hash}

async def submit_code_service(phone_number: str, code: str, db: AsyncSession):
    """
    Submit the verification code received on the phone number and finalize login.
    Use the same session stored during request_code_service.
    """
    user = await get_user_by_phone(phone_number, db)
    if user is None or not user.phone_code_hash or not user.session:
        raise ValueError("Phone number not found, code not requested, or no session stored. Request code first.")

    app = await get_current_app(db=db)
    api_id = app.api_id
    api_hash = app.api_hash

    # Recreate the client using the stored session from request_code_service
    temp_session = StringSession(user.session)
    client = TelegramClient(temp_session, api_id, api_hash)
    await client.connect()

    # Complete the login using the same session and code hash
    await client.sign_in(phone_number, code, phone_code_hash=user.phone_code_hash)
    session_string = client.session.save()

    # Fetch user info
    me = await client.get_me()
    my_user_id = me.id if me else None
    username = me.username if me else None

    # Update user with final session and clear phone_code_hash
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

    logging.info(f"User {phone_number} logged in successfully with username {username}.")

    # Start listening for messages in the background
    asyncio.create_task(start_listening_service(client, phone_number, db))

    return {"session": session_string}

async def start_listening_service(client: TelegramClient, phone_number: str, db: AsyncSession):
    """
    Start the event handler for new messages and run until disconnected.
    """
    init_event_handlers_service(client, db)
    try:
        await client.run_until_disconnected()
    except asyncio.CancelledError:
        logging.info(f"Stopped listening for {phone_number}")

def init_event_handlers_service(client: TelegramClient, db: AsyncSession):
    """
    Initialize all event handlers for the client.
    """
    @client.on(events.NewMessage(incoming=True))
    async def handle_new_message(event):
        await handle_new_message_service(event, client,db)

async def handle_new_message_service(event, client, db: AsyncSession):
    """
    Handle incoming private messages:
    - Log them to DB
    - Create a response and send it back
    """
    try:
        if event.is_private:
            print(f"Received event:{event}")
            me = await client.get_me()
            username = me.username
            sender = event.sender_id
            input_text = event.raw_text
            user = await get_user_by_username(username, db)

            # Save the message in the database
            log_entry = TelegramMessageLog(
                sender=str(sender),
                input_text=input_text
            )
            db.add(log_entry)
            await db.commit()

            logging.info(f"Message received from {sender}: {input_text}")

            # Generate a response (reversed text)
            print(f"UserBot: {user.bot_url}")
            response_text = await forward_message_to_service(user.bot_url, input_text)

            # Ensure response_text is valid
            if not response_text:
                logger.warning(f"No valid response received for input: {input_text}")
                response_text = "No response provided"

            # Update the response in the database
            log_entry.output_text = response_text
            db.add(log_entry)
            await db.commit()

            # Reply to the user
            await event.reply(response_text)
    except Exception as e:
        logging.error(f"Error handling message: {e}")
        raise e


async def forward_message_to_service(bot_url: str, input_text: str):
    """
    Sends the user's message to the external service and retrieves the response.
    """
    payload = {
        "platform": "telegram",
        "message_text": input_text
    }
    headers = {"Content-Type": "application/json"}

    # Configure connection pool limits and timeouts
    limits = httpx.Limits(max_connections=200, max_keepalive_connections=100)
    timeout = httpx.Timeout(10.0, connect=5.0, read=5.0, write=5.0)

    async with httpx.AsyncClient(limits=limits, timeout=timeout) as client:
        retries = 3  # Number of retries
        delay = 1  # Initial delay between retries in seconds

        for attempt in range(retries):
            try:
                # Send the POST request
                response = await client.post(bot_url, json=payload, headers=headers)

                logger.debug(f"Raw response status: {response.status_code}")
                logger.debug(f"Raw response text: {response.text}")

                # Ensure the response content is not empty before raising for status
                if not response.text:
                    logger.error(f"Empty response received from {bot_url}")
                    return "No response provided"

                logger.info(f"Received response from external service: {response}")
                # Parse the JSON response
                try:
                    result = response.json()
                    logger.info(f"Received response from external service: {result}")
                    return result.get("reply", "No reply provided")
                except ValueError as json_error:
                    logger.error(f"Failed to parse JSON response from {bot_url}: {json_error}")
                    logger.error(f"Raw response content: {response.text}")
                    return "Invalid response format"

            except httpx.HTTPStatusError as http_error:
                logger.error(
                    f"HTTP error from {bot_url} on attempt {attempt + 1}: {http_error.response.status_code} - {http_error.response.text}")
                if attempt < retries - 1:
                    await asyncio.sleep(delay * (2 ** attempt))  # Exponential backoff
                else:
                    return f"Error {http_error.response.status_code}: Service issue."

            except httpx.RequestError as req_error:
                logger.error(f"Request error while contacting {bot_url} on attempt {attempt + 1}: {req_error}")
                if attempt < retries - 1:
                    await asyncio.sleep(delay * (2 ** attempt))  # Exponential backoff
                else:
                    return "Service is unavailable. Please try again later."

            except Exception as e:
                logger.error(f"Unexpected error occurred on attempt {attempt + 1}: {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(delay * (2 ** attempt))  # Exponential backoff
                else:
                    return "Unexpected error occurred."

        return "Failed after multiple retries."
