import asyncio

import httpx
import logging

logging.basicConfig(level=logging.INFO)
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
            response.raise_for_status()
            logging.info(f"Message sent successfully to {recipient_id}: {response.json()}")
            return response.json()
        except httpx.RequestError as e:
            logging.error(f"Request error while sending Instagram message: {e}")
        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP error while sending Instagram message: {e.response.json()}")



async def forward_message_to_service(
    bot_url: str,
    page_access_token: str,
    page_id: str,
    sender_id: str,
    message_text: str,
):
    payload = {
        "platform": "instagram",
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
                await send_instagram_message(
                    page_token=page_access_token,
                    page_id=page_id,
                    recipient_id=sender_id,
                    message=result.get("reply", "No reply provided"),
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

