import logging
import requests
from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the router
whatsapp_api_router = APIRouter()

# Define a method to send a WhatsApp message using the Green API
def send_whatsapp_message(chat_id: str, message: str):
    """Send a WhatsApp message using the Green API."""
    url = "https://7103.api.greenapi.com/waInstance7103163078/sendMessage/d14dd7ae677f4808ac81b34635a82d3eb12d94e9a84d4ce381"
    payload = {
        "chatId": chat_id,
        "message": message
    }
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        logger.info(f"Message sent. Response: {response.text}")
        return response.json()
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return None

@whatsapp_api_router.post("/webhook", response_class=PlainTextResponse)
async def handle_webhook(request: Request):
    """Webhook endpoint that logs and prints the received payload."""
    try:
        # Get the JSON payload
        payload = await request.json()

        # Log and print the received payload
        logger.info(f"Received payload: {payload}")
        print(f"Received payload: {payload}")

        # Extract chatId and message from the payload
        chat_id = payload.get("chatId")
        message = payload.get("message")

        if chat_id and message:
            # Modify the message
            modified_message = f"Modified: {message}"

            # Send the modified message back
            send_response = send_whatsapp_message(chat_id, modified_message)

            # Log the response from the send API
            logger.info(f"Send message response: {send_response}")

            # Save the modified message (placeholder for database logic)
            # Example: Save to a database or a file
            logger.info(f"Message saved: Chat ID: {chat_id}, Modified Message: {modified_message}")

        # Respond with success
        return PlainTextResponse("Webhook processed and response sent.", status_code=200)

    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return PlainTextResponse("Failed to process webhook.", status_code=500)
