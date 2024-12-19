import logging
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database_setup import get_async_db
from src.whatsapp_api.service import forward_message_to_service
from src.whatsapp_api.schemas import CreateInstanceRequest
from src.tasks.create_instance_task import create_instance_task
from src.db.repositories.whatsapp_user_repositories import get_whatsapp_user


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the router
whatsapp_api_router = APIRouter()


@whatsapp_api_router.post("/webhook", response_class=PlainTextResponse)
async def handle_webhook(request: Request, db: AsyncSession = Depends(get_async_db)):
    try:
        # Get the JSON payload
        payload = await request.json()
        logger.info(f"Received payload: {payload}")

        # Extract idInstance
        instance_data = payload.get("instanceData")
        if not instance_data or "idInstance" not in instance_data:
            logger.error(f"Invalid payload structure: {payload}")
            return PlainTextResponse("idInstance not found in payload.", status_code=400)
        id_instance = instance_data.get("idInstance")
        if not id_instance:
            raise ValueError("idInstance not found in payload.")

        # Retrieve the WhatsApp user from the database
        user = await get_whatsapp_user(db, id_instance=id_instance)

        if not user:
            raise ValueError(f"No user found for idInstance '{id_instance}'.")

        # Check webhook type to avoid loops
        webhook_type = payload.get("typeWebhook")
        if webhook_type != "incomingMessageReceived":
            logger.info(f"Ignoring webhook of type: {webhook_type}")
            return PlainTextResponse("Webhook ignored.", status_code=200)

        # Extract chatId and message from the payload
        chat_id = payload.get("senderData", {}).get("chatId")
        message_data = payload.get("messageData", {}).get("extendedTextMessageData", {}).get("text")

        # Send the modified message using user's bot_url and API token
        send_response = await forward_message_to_service(
            bot_url=user.bot_url,  # User's bot URL
            chat_id=chat_id,
            message_text=message_data,
            api_url=user.api_url,  # API URL from the database
            id_instance=user.id_instance,  # Retrieved id_instance
            api_token_instance=user.api_token  # API token from the user
        )

        # Log the response from the send API
        logger.info(f"Send message response: {send_response}")

        # Respond with success
        return PlainTextResponse("Webhook processed and response sent.", status_code=200)

    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return PlainTextResponse("Failed to process webhook.", status_code=500)



@whatsapp_api_router.post("/create-instance-task")
def create_instance(request: Request, body: CreateInstanceRequest):
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
        raise HTTPException(status_code=500, detail=str(e))



