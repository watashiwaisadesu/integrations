import httpx
import logging
from src.utils.errors_handler import ExternalServiceError

logger = logging.getLogger(__name__)


async def send_instagram_message(page_token: str, page_id: str, recipient_id: str, message: str):
    """
    Sends a message to the customer via Instagram Graph API.
    """
    url = f"https://graph.instagram.com/v21.0/{page_id}/messages"

    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message},
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {page_token}",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            # Raises httpx.HTTPStatusError if status code >= 400
            response.raise_for_status()
            logger.info(f"Message sent successfully to {recipient_id}: {response.json()}")
            return response.json()

        except httpx.RequestError as e:
            # Any error in connecting to the server
            logger.error(f"Request error while sending Instagram message: {e}")
            raise ExternalServiceError(f"Request error while sending IG message: {e}") from e

        except httpx.HTTPStatusError as e:
            # Status code >= 400
            logger.error(f"HTTP error while sending Instagram message: {e.response.json()}")
            raise ExternalServiceError(
                f"HTTP error while sending IG message: {e.response.json()}"
            ) from e

#
# async def forward_message_to_service(
#     bot_id: str,
#     page_access_token: str,
#     page_id: str,
#     sender_id: str,
#     message_text: str,
# ):
#     payload = {
#         "platform": "instagram",
#         "message_text": message_text,
#     }
#     headers = {"Content-Type": "application/json"}
#
#     # Configure connection pool limits and timeouts
#     limits = httpx.Limits(max_connections=200, max_keepalive_connections=100)
#     timeout = httpx.Timeout(10.0, connect=5.0, read=5.0, write=5.0)
#
#     async with httpx.AsyncClient(limits=limits, timeout=timeout) as client:
#         retries = 3  # Number of retries
#         delay = 1    # Delay between retries (exponential backoff)
#
#         for attempt in range(retries):
#             try:
#                 response = await client.post(bot_id, json=payload, headers=headers)
#
#                 logger.debug(f"Raw response status: {response.status_code}")
#                 logger.debug(f"Raw response text: {response.text}")
#
#                 # If response body is empty, treat it as an error
#                 if not response.text:
#                     logger.error(f"Empty response received from {bot_id}")
#                     raise ExternalServiceError("Received empty response from external service")
#
#                 # Attempt to parse as JSON
#                 try:
#                     result = response.json()
#                     logger.info(f"Received response from external service: {result}")
#                 except ValueError as json_error:
#                     logger.error(f"Invalid JSON response from {bot_id}: {json_error}")
#                     logger.error(f"Raw response content: {response.text}")
#                     raise ExternalServiceError("Invalid JSON response from external service") from json_error
#
#                 # Send the external service's reply back to the user
#                 await send_instagram_message(
#                     page_token=page_access_token,
#                     page_id=page_id,
#                     recipient_id=sender_id,
#                     message=result.get("reply", "No reply provided"),
#                 )
#                 break  # Success! Exit the loop.
#
#             except httpx.HTTPStatusError as http_err:
#                 # The server responded with an error (status code >= 400)
#                 logger.error(
#                     f"HTTP error on attempt {attempt + 1}: {http_err.response.status_code} - {http_err.response.text}")
#                 if attempt < retries - 1:
#                     await asyncio.sleep(delay * (2 ** attempt))  # Exponential backoff
#                 else:
#                     raise ExternalServiceError(
#                         f"HTTP error after {retries} retries: {http_err.response.status_code}"
#                     ) from http_err
#
#             except httpx.RequestError as req_err:
#                 # Connection error, DNS error, etc.
#                 logger.error(f"Request error on attempt {attempt + 1}: {req_err}")
#                 if attempt < retries - 1:
#                     await asyncio.sleep(delay * (2 ** attempt))
#                 else:
#                     raise ExternalServiceError(
#                         f"Request error after {retries} retries: {req_err}"
#                     ) from req_err
#
#             except ExternalServiceError as e:
#                 # Already an external-service error; re-raise
#                 if attempt < retries - 1:
#                     logger.error(f"ExternalServiceError on attempt {attempt + 1}: {e}")
#                     await asyncio.sleep(delay * (2 ** attempt))
#                 else:
#                     raise
#
#             except Exception as e:
#                 # Any other unknown error
#                 logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
#                 if attempt < retries - 1:
#                     await asyncio.sleep(delay * (2 ** attempt))
#                 else:
#                     raise ExternalServiceError(f"Unexpected error after {retries} retries: {e}") from e
#
