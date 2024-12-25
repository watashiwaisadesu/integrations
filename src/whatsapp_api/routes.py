
import logging
from fastapi import APIRouter, Request, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database_setup import get_async_db
from src.whatsapp_api.service import forward_message_to_service
from src.whatsapp_api.schemas import CreateInstanceRequest
from src.tasks.create_instance_task import create_instance_task
from src.db.repositories.whatsapp_user_repositories import get_whatsapp_user

# Import your custom exceptions
from src.utils.errors_handler import (
    InvalidWebhookPayload,
    InternalServerError,
    InvalidQueryParameter,
)

logger = logging.getLogger(__name__)

whatsapp_api_router = APIRouter()


@whatsapp_api_router.post("/webhook", response_class=PlainTextResponse)
async def handle_webhook(request: Request, db: AsyncSession = Depends(get_async_db)):
    """
    Handle the incoming WhatsApp webhook and forward messages to an external service.
    """
    try:
        payload = await request.json()
        logger.info(f"Received payload: {payload}")

        # Validate payload structure
        instance_data = payload.get("instanceData")
        if not instance_data or "idInstance" not in instance_data:
            logger.error(f"Invalid payload structure: {payload}")
            raise InvalidWebhookPayload("idInstance not found in payload structure.")

        id_instance = instance_data.get("idInstance")
        if not id_instance:
            logger.error("idInstance missing in instanceData.")
            raise InvalidWebhookPayload("idInstance is None or empty.")

        # Retrieve the WhatsApp user
        user = await get_whatsapp_user(db, id_instance=id_instance)
        if not user:
            logger.error(f"No user found for idInstance '{id_instance}'.")
            raise InvalidQueryParameter(f"No user found for idInstance '{id_instance}'.")

        # Check webhook type
        webhook_type = payload.get("typeWebhook")
        if webhook_type != "incomingMessageReceived":
            logger.info(f"Ignoring webhook of type: {webhook_type}")
            return PlainTextResponse("Webhook ignored.", status_code=200)

        # Extract chatId and message
        chat_id = payload.get("senderData", {}).get("chatId")
        message_data = payload.get("messageData", {}).get("extendedTextMessageData", {}).get("text")

        # Forward the message
        send_response = await forward_message_to_service(
            bot_url=user.bot_url,
            chat_id=chat_id,
            message_text=message_data,
            api_url=user.api_url,
            id_instance=user.id_instance,
            api_token_instance=user.api_token
        )
        logger.info(f"Send message response: {send_response}")

        return PlainTextResponse("Webhook processed and response sent.", status_code=200)

    except InvalidWebhookPayload:
        # Re-raise so the custom 400 handler is triggered
        raise

    except InvalidQueryParameter:
        # Re-raise so the custom 422 handler is triggered
        raise

    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        # Convert to our custom 500-level exception
        raise InternalServerError("Failed to process webhook.") from e


@whatsapp_api_router.post("/create-instance-task")
def create_instance(request: Request, body: CreateInstanceRequest):
    """
    Create a new WhatsApp instance (via Celery task).
    """
    try:
        # Retrieve the base URL from the request object
        base_url = str(request.base_url)
        callback_url = base_url + "v1/whatsapp/webhook"
        print(callback_url)

        # Queue the task with the generated callback_url
        task = create_instance_task.delay(
            body.email,
            body.password,
            callback_url
        )
        return {"status": "Task queued", "task_id": task.id}
    except Exception as e:
        logger.error(f"Error in create_instance: {e}")
        # Could re-raise a custom exception or 500-level if you want
        raise InternalServerError("Failed to create WhatsApp instance task.") from e



