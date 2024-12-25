from fastapi import APIRouter, Request, Query, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from celery.result import AsyncResult

from src.tasks.app_setup_task import app_setup_task
from src.core.celery_setup import celery
import logging

from src.core.database_setup import get_async_db
from src.db.repositories.instagram_app_repositories import (
    get_instagram_credentials,
    get_app_verify_token
)
from src.db.repositories.instagram_user_repositories import (
    create_instagram_account,
    get_instagram_account
)
from src.db.repositories.external_service_app_repositories import get_app_external_service_base_url
from src.instagram_api.utils import extract_code_from_url
from src.instagram_api.schemas import (
    WebhookObject,
    AppSetupRequest,
)
from src.instagram_api.token import InstagramAuth
from src.instagram_api.user import get_instagram_user_info
from src.instagram_api.service import forward_message_to_service
from src.external_service.service import create_bot_request

# Import your custom exceptions
from src.utils.errors_handler import (
    VerificationTokenMismatch,
    InvalidWebhookPayload,
    InternalServerError,
)


logger = logging.getLogger(__name__)

instagram_api_router = APIRouter()


@instagram_api_router.get("/instagram_details")
async def get_instagram_details(
        db: AsyncSession = Depends(get_async_db)
):
    logger.info("Fetching Instagram credentials from DB")
    return await get_instagram_credentials(db)


@instagram_api_router.get("/handle_code")
async def handle_code(
        request: Request,
        db: AsyncSession = Depends(get_async_db)
):
    try:
        logger.info("Starting handle_code process")
        instagram_app_id, instagram_app_secret = await get_instagram_credentials(db, return_type="credentials")
        external_service_base_url = await get_app_external_service_base_url(db)
        redirect_uri, code = extract_code_from_url(str(request.url))
        # Initialize the InstagramAuth class
        instagram_auth = InstagramAuth(
            client_id=instagram_app_id,
            client_secret=instagram_app_secret,
            redirect_uri=redirect_uri
        )
        short_lived_token = instagram_auth.get_short_access_token(code)
        print(short_lived_token)
        long_lived_token = instagram_auth.get_long_lived_access_token(short_lived_token)
        user = get_instagram_user_info(long_lived_token)
        username= user['username']
        user_id = user['user_id']
        external_service_base_url = await get_app_external_service_base_url(db)

        logger.info(f"Instagram user {username} retrieved successfully")

        bot_url = await create_bot_request(username, external_service_base_url, True)
        if not bot_url:
            logger.error("Failed to create bot URL.")
            raise InternalServerError()
        await create_instagram_account(db, username, user_id, long_lived_token, bot_url)
        logger.info("Instagram account created and connected successfully.")
        return "Your account is now connected to service!"
    except InternalServerError:
        # Re-raise so our custom handler catches it
        raise
    except Exception as e:
        # If you want to always handle unknown exceptions as InternalServerError, do:
        logger.error(f"Unhandled exception in handle_code: {str(e)}")
        raise InternalServerError()


# Webhook Verification Endpoint
@instagram_api_router.get("/webhook", response_class=PlainTextResponse)
async def verify_token(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    db: AsyncSession = Depends(get_async_db)
):
    logger.info(
        f"Verification request received: mode={hub_mode}, token={hub_verify_token}, challenge={hub_challenge}"
    )
    verify_token = await get_app_verify_token(db)
    if hub_mode == "subscribe" and hub_verify_token == verify_token:
        logger.info("Verification token matches; returning hub_challenge")
        return hub_challenge  # Return challenge as plain text
    logger.error("Verification token mismatch.")
    raise VerificationTokenMismatch()


# Webhook Event Handler Endpoint
@instagram_api_router.post("/webhook")
async def handle_webhook(
        request: Request,
        db: AsyncSession = Depends(get_async_db)
):
    try:
        data = await request.json()
        logger.info(f"Webhook event received: {data}")

        try:
            webhook_event = WebhookObject(**data)
        except Exception as e:
            logger.error(f"Error parsing webhook data: {e}")
            raise InvalidWebhookPayload()

        if webhook_event.object != "instagram":
            logger.warning("Non-instagram webhook object received.")
            # Optionally do nothing or raise an exception
            pass

        for entry in webhook_event.entry:
            page_id = entry.id  # Extract the page_id dynamically
            page = await get_instagram_account(db, page_id)
            if page is None:
                logger.warning(f"No matching Instagram account for page_id: {page_id}")
                continue
            page_access_token = page.access_token
            page_bot_url = page.bot_url
            for messaging_event in entry.messaging:
                # Skip messages that are echoes
                if messaging_event.message.get("is_echo"):
                    logger.info(f"Skipping echo message: {messaging_event.message}")
                    continue

                sender_id = messaging_event.sender.get("id")
                message_text = messaging_event.message.get("text")

                if message_text:
                    logger.info(
                        f"Forwarding message to external service: {message_text} from {sender_id}"
                    )
                    await forward_message_to_service(
                        bot_url=page_bot_url,
                        page_access_token=page_access_token,
                        page_id=page_id,
                        sender_id=sender_id,
                        message_text=message_text,
                    )
        return {"status": "success"}
    except InvalidWebhookPayload:
        # Re-raise so the custom handler catches it
        raise
    except Exception as e:
        logger.error(f"Unhandled exception in handle_webhook: {str(e)}")
        # Convert to our custom InternalServerError
        raise InternalServerError()


@instagram_api_router.post("/app-setup")
def app_setup(request: Request, body: AppSetupRequest):
    try:
        # Retrieve the base URL from the request object
        callback_url = str(request.base_url)
        logger.info(f"Callback URL: {callback_url}")

        # Queue the task with the generated callback_url
        task = app_setup_task.delay(
            body.email,
            body.password,
            body.verify_token,
            callback_url,
            body.app_name,
        )
        logger.info(f"App setup task queued with ID: {task.id}")
        return {"status": "Task queued", "task_id": task.id}
    except Exception as e:
        logger.error(f"Error in app_setup: {str(e)}")
        raise InternalServerError()


@instagram_api_router.get("/task-status/{task_id}")
def get_task_status(task_id: str):
    try:
        # Retrieve the task result using the task_id
        task_result = AsyncResult(task_id, app=celery)
        logger.info(f"Fetched task status for {task_id}: {task_result.state}")

        # Check the task status
        if task_result.state == "PENDING":
            return {"status": "pending", "message": "Task is still being processed."}
        elif task_result.state == "SUCCESS":
            return {"status": "success", "result": task_result.result}
        elif task_result.state == "FAILURE":
            return {"status": "failure", "message": str(task_result.result)}
        else:
            return {"status": task_result.state, "message": "Task is in progress."}
    except Exception as e:
        logger.error(f"Error fetching task status: {str(e)}")
        raise InternalServerError()




