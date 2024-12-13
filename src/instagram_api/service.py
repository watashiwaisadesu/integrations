import httpx
import logging
from collections import defaultdict
import asyncio

# Dictionary to hold queues for each sender
message_queues = defaultdict(asyncio.Queue)

# Lock to prevent race conditions when creating workers
queue_locks = defaultdict(asyncio.Lock)


async def enqueue_message(sender_id: str, page_id: str, page_access_token: str, message_text: str):
    queue = message_queues[sender_id]
    await queue.put((page_id, page_access_token, message_text))

    # Start a worker for the queue if it doesn't already exist
    async with queue_locks[sender_id]:
        if not any(task for task in asyncio.all_tasks() if task.get_name() == f"worker-{sender_id}"):
            asyncio.create_task(process_queue(sender_id), name=f"worker-{sender_id}")


async def process_queue(sender_id: str):
    queue = message_queues[sender_id]
    while not queue.empty():
        page_id, page_access_token, message_text = await queue.get()
        print(page_id, page_access_token, message_text)
        try:
            # Send message to external service and handle response
            await forward_message_to_service(
                external_service_url="https://cf9a0fdb86e838aebcbc2616526072f1.serveo.net",
                page_access_token=page_access_token,
                page_id=page_id,
                sender_id=sender_id,
                message_text=message_text,
            )
        except Exception as e:
            logging.error(f"Error processing message for sender {sender_id}: {e}")
        finally:
            queue.task_done()



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

