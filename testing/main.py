import asyncio
import logging
from collections import defaultdict
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# Dictionary to hold queues for each sender
message_queues = defaultdict(asyncio.Queue)

# Lock to prevent race conditions when creating workers
queue_locks = defaultdict(asyncio.Lock)


async def enqueue_message(sender_id: str, page_id: str, page_access_token: str, message_text: str):
    """
    Add a message to the sender's queue and start a worker for the sender if not already running.
    """
    queue = message_queues[sender_id]
    await queue.put((page_id, page_access_token, message_text))

    async with queue_locks[sender_id]:
        # Check if a worker for this sender is already running
        if not any(task for task in asyncio.all_tasks() if task.get_name() == f"worker-{sender_id}"):
            asyncio.create_task(process_queue(sender_id), name=f"worker-{sender_id}")


async def process_queue(sender_id: str):
    """
    Process messages for a given sender in order.
    """
    queue = message_queues[sender_id]
    while not queue.empty():
        page_id, page_access_token, message_text = await queue.get()
        try:
            # Simulate forwarding the message and receiving a response
            await forward_message_to_service(
                page_access_token=page_access_token,
                page_id=page_id,
                sender_id=sender_id,
                message_text=message_text,
            )
        except Exception as e:
            logging.error(f"Error processing message for sender {sender_id}: {e}")
        finally:
            queue.task_done()


async def forward_message_to_service(page_access_token: str, page_id: str, sender_id: str, message_text: str):
    """
    Simulate sending a message to an external service and getting a response after a random delay.
    """
    delay = random.randint(1, 10)  # Random delay between 1 and 10 seconds
    logging.info(f"Simulating delay of {delay} seconds for message: {message_text}")
    await asyncio.sleep(delay)  # Simulate processing time

    # Simulate a response from the external service
    response_text = f"Response to '{message_text}'"
    logging.info(f"Received simulated response for sender {sender_id}: {response_text}")

    # Send the response back to the user
    await send_message(
        page_token=page_access_token,
        page_id=page_id,
        recipient_id=sender_id,
        message_text=response_text,
    )


async def send_message(page_token: str, page_id: str, recipient_id: str, message_text: str):
    """
    Simulate sending a message back to the recipient.
    """
    logging.info(f"Sending message to {recipient_id}: {message_text}")
    # Simulate a successful send
    await asyncio.sleep(1)  # Simulate API call latency
    logging.info(f"Message to {recipient_id} sent successfully!")


async def main():
    """
    Entry point to test the message processing system.
    """
    # Simulate incoming messages
    await asyncio.gather(
        enqueue_message("sender1", "page1", "token1", "Hello!"),
        enqueue_message("sender1", "page1", "token1", "How are you?"),
        enqueue_message("sender1", "page1", "token1", "Tell me more!"),
        enqueue_message("sender2", "page1", "token2", "Hi!"),
        enqueue_message("sender2", "page1", "token2", "I need help!"),
    )

    # Allow some time for processing
    await asyncio.sleep(20)


if __name__ == "__main__":
    asyncio.run(main())
