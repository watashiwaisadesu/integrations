import asyncio
import logging
import httpx
import requests

from src.utils.errors_handler import ExternalServiceError  # Import your custom exception

logger = logging.getLogger(__name__)


async def send_whatsapp_message(chat_id: str, message: str, api_url: str, id_instance: str, api_token_instance: str):
    """
    Send a WhatsApp message using the Green API (synchronous call).
    """
    url = f"{api_url}/waInstance{id_instance}/sendMessage/{api_token_instance}"
    payload = {"chatId": chat_id, "message": message}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        # You may check if response.status_code >= 400 and raise your custom exception as well:
        if response.status_code >= 400:
            logger.error(f"Error sending WhatsApp message (HTTP {response.status_code}): {response.text}")
            raise ExternalServiceError(
                f"Failed to send WhatsApp message. Status code: {response.status_code}, "
                f"Response: {response.text}"
            )
        logger.info(f"Message sent. Response: {response.text}")
        return response.json()
    except requests.RequestException as e:
        logger.error(f"RequestException when sending message via Green API: {e}")
        raise ExternalServiceError("Network error while sending WhatsApp message.") from e
    except Exception as e:
        logger.error(f"Unexpected error sending message: {e}")
        raise ExternalServiceError("Unexpected error while sending WhatsApp message.") from e



#
# async def forward_message_to_service(
#     bot_url: str,
#     chat_id: str,
#     api_url: str,
#     id_instance: str,
#     api_token_instance: str,
#     message_text: str = None,
# ):
#     """
#     Forward incoming WhatsApp message to an external service (bot_url),
#     parse the result, then send a response back via the Green API.
#     """
#     payload = {"platform": "whatsapp", "message_text": message_text}
#     headers = {"Content-Type": "application/json"}
#
#     # Configure connection pool limits and timeouts
#     limits = httpx.Limits(max_connections=200, max_keepalive_connections=100)
#     timeout = httpx.Timeout(10.0, connect=5.0, read=5.0, write=5.0)
#
#     retries = 3
#     delay = 1  # initial delay, used with exponential backoff
#
#     async with httpx.AsyncClient(limits=limits, timeout=timeout) as client:
#         for attempt in range(retries):
#             try:
#                 response = await client.post(bot_url, json=payload, headers=headers)
#
#                 logger.debug(f"Attempt {attempt + 1}: status={response.status_code}, text={response.text}")
#
#                 # Check if response text is empty
#                 if not response.text:
#                     logger.error(f"Empty response received from {bot_url}")
#                     raise ExternalServiceError("Empty response from external service")
#
#                 # Attempt to parse the JSON
#                 try:
#                     result = response.json()
#                     logger.info(f"Received response from external service: {result}")
#                 except ValueError as json_error:
#                     logger.error(f"Invalid JSON from {bot_url}: {json_error}")
#                     logger.error(f"Raw response content: {response.text}")
#                     raise ExternalServiceError("Invalid JSON format from external service") from json_error
#
#                 # Send the external service's reply back to the user
#                 reply_text = result.get("reply", "No reply provided")
#                 await send_whatsapp_message(
#                     chat_id=chat_id,
#                     message=reply_text,
#                     api_url=api_url,
#                     id_instance=id_instance,
#                     api_token_instance=api_token_instance,
#                 )
#                 break  # Exit on success
#
#             except httpx.HTTPStatusError as http_err:
#                 logger.error(
#                     f"HTTP error on attempt {attempt + 1}: "
#                     f"{http_err.response.status_code} - {http_err.response.text}"
#                 )
#                 if attempt < retries - 1:
#                     await asyncio.sleep(delay * (2 ** attempt))
#                 else:
#                     # Raise a custom error
#                     raise ExternalServiceError(
#                         f"HTTP error after {retries} retries: "
#                         f"{http_err.response.status_code} - {http_err.response.text}"
#                     ) from http_err
#
#             except httpx.RequestError as req_err:
#                 logger.error(f"Request error on attempt {attempt + 1}: {req_err}")
#                 if attempt < retries - 1:
#                     await asyncio.sleep(delay * (2 ** attempt))
#                 else:
#                     raise ExternalServiceError("Service unavailable after multiple retries.") from req_err
#
#             except ExternalServiceError as e:
#                 # If we already raised an ExternalServiceError (e.g., empty response),
#                 # we handle it similarly with a retry.
#                 logger.error(f"ExternalServiceError on attempt {attempt + 1}: {e}")
#                 if attempt < retries - 1:
#                     await asyncio.sleep(delay * (2 ** attempt))
#                 else:
#                     raise
#
#             except Exception as e:
#                 logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
#                 if attempt < retries - 1:
#                     await asyncio.sleep(delay * (2 ** attempt))
#                 else:
#                     raise ExternalServiceError("Unexpected error after multiple retries.") from e
#
