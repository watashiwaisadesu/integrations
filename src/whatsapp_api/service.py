import asyncio

import requests
import logging
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Define a method to send a WhatsApp message using the Green API
async def send_whatsapp_message(chat_id: str, message: str,api_url: str, id_instance: str, api_token_instance: str):
    """Send a WhatsApp message using the Green API."""
    url = f"{api_url}/waInstance{id_instance}/sendMessage/{api_token_instance}"
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


async def forward_message_to_service(
    bot_url: str,
    chat_id: str,
    api_url: str,
    id_instance: str,
    api_token_instance: str,
    message_text: str = None,
):
    payload = {
        "platform": "whatsapp",
        "message_text": message_text,
    }
    headers = {"Content-Type": "application/json"}

    # Configure connection pool limits and timeouts
    limits = httpx.Limits(max_connections=200, max_keepalive_connections=100)
    timeout = httpx.Timeout(10.0, connect=5.0, read=5.0, write=5.0)

    async with httpx.AsyncClient(limits=limits, timeout=timeout) as client:
        retries = 3  # Number of retries
        delay = 1  # Delay between retries (exponential backoff will apply)

        for attempt in range(retries):
            try:
                # Send the POST request
                response = await client.post(bot_url, json=payload, headers=headers)

                # Log the raw response for debugging
                logger.debug(f"Raw response status: {response.status_code}")
                logger.debug(f"Raw response text: {response.text}")

                # Ensure the response content is not empty before raising for status
                if not response.text:
                    logger.error(f"Empty response received from {bot_url}")
                    return None

                logger.info(f"Received response from external service: {response}")
                # Parse the JSON response
                try:
                    result = response.json()
                    logger.info(f"Received response from external service: {result}")
                except ValueError as json_error:
                    logger.error(f"Invalid JSON response from {bot_url}: {json_error}")
                    logger.error(f"Raw response content: {response.text}")
                    return None

                # Send the external service's response back to the user
                await send_whatsapp_message(
                    chat_id=chat_id,
                    message=result.get("reply", "No reply provided"),
                    api_url=api_url,
                    id_instance=id_instance,
                    api_token_instance=api_token_instance,
                )
                break  # Exit loop on success

            except httpx.HTTPStatusError as http_err:
                logger.error(
                    f"HTTP error occurred on attempt {attempt + 1}: {http_err.response.status_code} - {http_err.response.text}")
                if attempt < retries - 1:
                    await asyncio.sleep(delay * (2 ** attempt))  # Exponential backoff
                else:
                    raise http_err

            except httpx.RequestError as req_err:
                logger.error(f"Request error occurred on attempt {attempt + 1}: {req_err}")
                if attempt < retries - 1:
                    await asyncio.sleep(delay * (2 ** attempt))  # Exponential backoff
                else:
                    raise req_err

            except Exception as e:
                logger.error(f"Unexpected error occurred on attempt {attempt + 1}: {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(delay * (2 ** attempt))  # Exponential backoff
                else:
                    raise e

