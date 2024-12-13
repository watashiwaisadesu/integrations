from fastapi import APIRouter, Request, HTTPException, Query, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from src.core.database_setup import get_async_db
from src.db.repositories.instagram_app_repositories import (
    get_instagram_credentials
)
from src.db.repositories.instagram_user_repositories import (
    create_instagram_account,
    get_instagram_account
)
from src.instagram_api.utils import extract_code_from_url
from src.instagram_api.schemas import WebhookObject
from src.instagram_api.token import InstagramAuth
from src.instagram_api.user import get_instagram_user_info
from src.instagram_api.service import enqueue_message, forward_message_to_service

logging.basicConfig(level=logging.INFO)

instagram_api_router = APIRouter()


@instagram_api_router.get("/instagram_details")
async def save_instagram_details(
        db: AsyncSession = Depends(get_async_db)
):
    return await get_instagram_credentials(db)


@instagram_api_router.get("/handle_code")
async def handle_code(
        request: Request,
        db: AsyncSession = Depends(get_async_db)
):
    instagram_app_id, instagram_app_secret = await get_instagram_credentials(db, return_type="credentials")
    redirect_uri, code = extract_code_from_url(str(request.url))
    # Initialize the InstagramAuth class
    instagram_auth = InstagramAuth(
        client_id=instagram_app_id,
        client_secret=instagram_app_secret,
        redirect_uri=redirect_uri
    )
    short_lived_token = instagram_auth.get_short_access_token(code)
    long_lived_token = instagram_auth.get_long_lived_access_token(short_lived_token)
    user = get_instagram_user_info(long_lived_token)
    username= user['username']
    user_id = user['user_id']
    await create_instagram_account(db, username, user_id, long_lived_token)
    return "Your account is now connected to service!"


# Webhook Verification Endpoint
@instagram_api_router.get("/webhook", response_class=PlainTextResponse)
async def verify_token(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    db: AsyncSession = Depends(get_async_db)
):
    logging.info(f"Verification request received: mode={hub_mode}, token={hub_verify_token}, challenge={hub_challenge}")
    verify_token, callback_url = await get_instagram_credentials(db, return_type="webhook_details")
    if hub_mode == "subscribe" and hub_verify_token == verify_token:
        return hub_challenge  # Return challenge as plain text
    raise HTTPException(status_code=403, detail="Verification token mismatch")


# Webhook Event Handler Endpoint
@instagram_api_router.post("/webhook")
async def handle_webhook(
        request: Request,
        db: AsyncSession = Depends(get_async_db)
):
    data = await request.json()
    logging.info(f"Webhook event received: {data}")

    try:
        webhook_event = WebhookObject(**data)
    except Exception as e:
        logging.error(f"Error parsing webhook data: {e}")
        raise HTTPException(status_code=400, detail="Invalid webhook payload")

    if webhook_event.object != "instagram":
        return
    for entry in webhook_event.entry:
        page_id = entry.id  # Extract the page_id dynamically
        page = await get_instagram_account(db, page_id)
        if page is None:
            continue
        page_access_token = page.access_token
        for messaging_event in entry.messaging:
            # Skip messages that are echoes
            if messaging_event.message.get("is_echo"):
                logging.info(f"Skipping echo message: {messaging_event.message}")
                continue

            sender_id = messaging_event.sender.get("id")
            message_text = messaging_event.message.get("text")

            if message_text:
                logging.info(f"Forwarding message to external service: {message_text} from {sender_id}")
                # await enqueue_message(sender_id, page_id, page_access_token, message_text)
                await forward_message_to_service(
                    external_service_url="https://b87976f0f549bf7aeac4404d90db6ef0.serveo.net/process",
                    page_access_token=page_access_token,
                    page_id=page_id,
                    sender_id=sender_id,
                    message_text=message_text,
                )
    return {"status": "success"}

