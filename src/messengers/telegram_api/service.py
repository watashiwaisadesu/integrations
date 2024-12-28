import asyncio
import logging
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from sqlalchemy.ext.asyncio import AsyncSession

from src.bots.openai.service import handle_incoming_message
from src.db.repositories.telegram_app_repositories import (
    get_current_app
)
from src.db.repositories.telegram_user_repositories import (
    add_or_update_telegram_user,
    get_user_by_phone,
    get_telegram_user_by_id,
)
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
        user_id = me.id if me else None
        username = me.username if me else None

        await add_or_update_telegram_user(
            phone_number=phone_number,
            db=db,
            session=session_string,
            username=username,
            user_id=str(user_id),
            phone_code_hash=None,
            bot_id=None,
        )

        logger.info(f"User {phone_number} logged in successfully with username={username}.")
        asyncio.create_task(start_listening_service(client, phone_number, db))

        return  user_id

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
            print("listenTGinside")
            logger.debug(f"New private message event: {event}")
            me = await client.get_me()
            user_id = me.id if me else "unknown_userid"
            sender_id = event.sender_id
            message_text = event.raw_text

            user = await get_telegram_user_by_id(db, user_id)
            if not user:
                logger.warning(f"No DB user record found for Telegram user_id={user_id}")
            assistant_id = user.bot_id

            logger.info(f"Message received from {sender_id}: {message_text}")

            response = await handle_incoming_message(
                        db=db,
                        sender_id=sender_id,
                        owner_id=user_id,
                        assistant_id=assistant_id,
                        message=message_text,
                        platform="telegram",
                    )
            # Fallback if no valid response
            if not response['response']:
                logger.warning(f"No valid response received for input: {message_text}")
                response = "No response provided"

            # Reply to the user in Telegram
            await event.reply(response['response'])

    except Exception as e:
        logger.error(f"Error handling message from {event.sender_id}: {e}")
        # If you want a 500 in API routes triggered by a webhook, raise a custom TelegramMessageHandlingError.
        # If this code is purely background (not in a FastAPI route), you can log or re-raise as you wish.
        raise TelegramMessageHandlingError("Error in handle_new_message_service") from e

