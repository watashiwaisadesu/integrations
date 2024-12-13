import asyncio
import logging

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.telegram_models import MessageLog
from src.db.repositories.telegram_app_repositories import (
    upsert_telegram_app,
    get_current_app
)
from src.db.repositories.telegram_user_repositories import (
    add_or_update_telegram_user,
    get_user_by_phone,
)


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
    username = me.username if me and me.username else str(me.id)

    # Update user with final session and clear phone_code_hash
    await add_or_update_telegram_user(
        phone_number=phone_number,
        db=db,
        session=session_string,
        username=username,
        phone_code_hash=None
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
        await handle_new_message_service(event, db)

async def handle_new_message_service(event, db: AsyncSession):
    """
    Handle incoming private messages:
    - Log them to DB
    - Create a response and send it back
    """
    try:
        if event.is_private:
            sender = event.sender_id
            input_text = event.raw_text

            # Save the message in the database
            log_entry = MessageLog(
                sender=str(sender),
                input_text=input_text
            )
            db.add(log_entry)
            await db.commit()

            logging.info(f"Message received from {sender}: {input_text}")

            # Generate a response (reversed text)
            output_text = input_text[::-1]

            # Update the response in the database
            log_entry.output_text = output_text
            db.add(log_entry)
            await db.commit()

            # Reply to the user
            await event.reply(output_text)
    except Exception as e:
        logging.error(f"Error handling message: {e}")
