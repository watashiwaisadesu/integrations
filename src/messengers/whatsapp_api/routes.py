import asyncio
import logging
import httpx
from fastapi import APIRouter, Request, Depends, WebSocket, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from celery.result import AsyncResult

from src.bots.openai.service import handle_incoming_message
from src.core.celery_setup import celery

from src.core.database_setup import get_async_db
from src.messengers.whatsapp_api.service import send_whatsapp_message
from src.messengers.whatsapp_api.schemas import CreateInstanceRequest
from src.tasks.create_instance_task import create_instance_task
from src.db.repositories.whatsapp_user_repositories import (
    get_whatsapp_user_by_id,
    update_whatsapp_user_bot_id,
    update_whatsapp_user_phone
)
from src.utils.errors_handler import (
    InvalidWebhookPayload,
    InternalServerError,
    InvalidQueryParameter,
)

logger = logging.getLogger(__name__)

whatsapp_api_router = APIRouter()


@whatsapp_api_router.post("/webhook", response_class=PlainTextResponse)
async def handle_whatsapp_webhook(
    request: Request,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Handle the incoming WhatsApp webhook and process messages.
    """
    try:
        data = await request.json()
        logger.info(f"Webhook event received: {data}")

        # Validate payload structure
        instance_data = data.get("instanceData")
        if not instance_data or "idInstance" not in instance_data:
            logger.error(f"Invalid payload structure: {data}")
            raise InvalidWebhookPayload("idInstance not found in payload structure.")

        id_instance = instance_data.get("idInstance")
        owner = instance_data.get("wid")
        if not id_instance:
            logger.error("idInstance missing in instanceData.")
            raise InvalidWebhookPayload("idInstance is None or empty.")

        # Retrieve the WhatsApp user
        user = await get_whatsapp_user_by_id(db, id_instance=str(id_instance))
        if not user:
            logger.warning(f"No user found for idInstance '{id_instance}'. Skipping webhook.")
            return PlainTextResponse("No user found for idInstance.", status_code=404)

        assistant_id = user.bot_id
        api_url = user.api_url  # Make sure the user object contains the api_url
        api_token_instance = user.api_token  # And the api_token_instance

        # Check webhook type
        webhook_type = data.get("typeWebhook")
        if webhook_type != "incomingMessageReceived":
            logger.info(f"Ignoring webhook of type: {webhook_type}")
            return PlainTextResponse("Webhook ignored.", status_code=200)

        # Extract phone number and message
        sender_data = data.get("senderData", {})
        chat_id = sender_data.get("chatId")  # Use chatId from senderData
        sender = sender_data.get("sender")
        if not chat_id:
            logger.warning(f"No chatId found in senderData: {sender_data}")
            return PlainTextResponse("Sender chatId missing.", status_code=422)

        message_data = data.get("messageData", {}).get("extendedTextMessageData", {}).get("text")
        if not message_data:
            logger.info("No text message found. Skipping processing.")
            return PlainTextResponse("No text message to process.", status_code=200)

        # Process the incoming message
        logger.info(f"Processing message from {chat_id}: {message_data}")
        response = await handle_incoming_message(
            db=db,
            sender_id=sender,  # Use chatId as sender_id
            owner_id=owner,
            assistant_id=assistant_id,
            message=message_data,
            platform="whatsapp",
        )

        logger.info(f"Response for sender {chat_id}: {response['response']}")

        # Send the response back to the sender via WhatsApp
        await send_whatsapp_message(
            chat_id=chat_id,  # No need to format this as it's already in the correct format
            message=response["response"],
            api_url=api_url,
            id_instance=id_instance,
            api_token_instance=api_token_instance,
        )

        return PlainTextResponse("Webhook processed and response sent.", status_code=200)

    except InvalidWebhookPayload:
        # Re-raise so the custom handler catches it
        raise

    except Exception as e:
        logger.error(f"Unhandled exception in handle_whatsapp_webhook: {str(e)}")
        # Convert to our custom InternalServerError
        raise InternalServerError("Failed to process WhatsApp webhook.") from e


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



@whatsapp_api_router.get("/task-status/{task_id}")
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



@whatsapp_api_router.websocket("/ws/qr-status/{id_instance}/{api_token}")
async def websocket_endpoint(websocket: WebSocket, id_instance: str, api_token: str, db: AsyncSession = Depends(get_async_db)):
    """
    WebSocket to track the QR code scanning status.
    """
    api_url = 'https://7103.api.greenapi.com'
    await websocket.accept()
    try:
        url = f"{api_url}/waInstance{id_instance}/getWaSettings/{api_token}"
        while True:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                if response.status_code != 200:
                    raise HTTPException(status_code=response.status_code, detail="Failed to fetch WhatsApp settings")

                data = response.json()
                state_instance = data.get("stateInstance")


                if state_instance == "authorized":
                    # Send a message that QR code is scanned successfully and include redirection URL
                    phone_number = data.get("phone")
                    await update_whatsapp_user_phone(db,id_instance,phone_number)
                    await websocket.send_json({
                        "status": "scanned",
                        "message": "QR code scanned successfully!",
                        "redirect": f"/v1/bot/bot_creation/whatsapp/{id_instance}"
                    })
                    break  # Break the loop after sending the successful state
                elif state_instance == "notAuthorized":
                    await websocket.send_json({"status": "pending", "message": "QR code not yet scanned."})
                else:
                    await websocket.send_json({"status": "unknown", "message": f"Current state: {state_instance}"})

            await asyncio.sleep(2)  # Poll every 2 seconds
    except Exception as e:
        await websocket.close(reason=str(e))












