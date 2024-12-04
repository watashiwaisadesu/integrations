from fastapi import APIRouter, Request, HTTPException, Query, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
import logging

from src.core.database_setup import get_async_db
from src.db.repositories.app_repositories import (
    set_instagram_credentials,
    get_webhook_details,
    get_instagram_credentials
)
from src.db.repositories.instagram_account_repositories import (
    create_instagram_account,
    get_instagram_account
)
from src.instagram_api.utils import extract_code_from_url
from src.instagram_api.schemas import WebhookObject
from src.instagram_api.token import InstagramAuth
from src.instagram_api.user import get_instagram_user_info


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
    verify_token_str, callback_url = await get_webhook_details(db)
    if hub_mode == "subscribe" and hub_verify_token == verify_token_str:
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

    if webhook_event.object == "instagram":
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
                    await forward_message_to_service(
                        external_service_url="https://17f08005521d190ebd92a7086c9bba02.serveo.net/process",
                        page_access_token=page_access_token,
                        page_id=page_id,
                        sender_id=sender_id,
                        message_text=message_text,
                    )
                    # response_message = f"Your message: {message_text}"
                    # await send_message(page_access_token, page_id, sender_id, response_message)

    return {"status": "success"}


async def forward_message_to_service(
    external_service_url: str,
    page_access_token: str,
    page_id: str,
    sender_id: str,
    message_text: str,
):
    """
    Sends the received message to an external service and awaits its response.
    """
    payload = {
        "page_id": page_id,
        "sender_id": sender_id,
        "message_text": message_text,
    }

    headers = {"Content-Type": "application/json"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(external_service_url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            logging.info(f"Received response from external service: {result}")

            # Send the external service's response back to the user
            await send_message(
                page_token=page_access_token,
                page_id=page_id,
                recipient_id=sender_id,
                message_text=result.get("reply", "No reply provided"),
            )
        except httpx.RequestError as e:
            logging.error(f"Request error while sending to external service: {e}")
        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP error from external service: {e.response.json()}")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")


async def send_message(page_token: str, page_id: str, recipient_id: str, message_text: str):
    """
    Sends a message to the customer via Instagram Graph API.
    """
    url = f"https://graph.instagram.com/v21.0/{page_id}/messages"

    # Create payload
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text},
    }

    # Add access token in headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {page_token}",
    }

    # Make POST request to Instagram Graph API
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            logging.info(f"Message sent successfully to {recipient_id}: {response.json()}")
            return response.json()
        except httpx.RequestError as e:
            logging.error(f"Request error while sending message: {e}")
        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP error while sending message: {e.response.json()}")

