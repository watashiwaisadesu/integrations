# src/bot/message_handler.py
from sys import platform

from sqlalchemy.ext.asyncio import AsyncSession
from src.db.repositories.thread_repositories import get_thread, save_thread
from src.bots.openai.assistant_manager import AssistantManager
import logging

logger = logging.getLogger(__name__)


async def handle_incoming_message(
    db: AsyncSession,
    sender_id: str,
    owner_id: str,
    assistant_id: str,
    message: str,
    platform: str
):
    """
    Handles incoming messages:
    1. Check if a thread exists for sender_id and owner_id.
    2. Create a new thread if none exists.
    3. Forward the message to OpenAI and wait for the assistant's response.
    """
    try:
        # Step 1: Initialize AssistantManager with the assistant_id
        assistant_manager = AssistantManager()
        assistant_manager.set_assistant(assistant_id)

        # Step 2: Check for existing thread in the database
        thread = await get_thread(db, str(sender_id), str(owner_id), platform)

        if not thread:
            # Step 3: Create a new thread using AssistantManager
            thread_id = assistant_manager.create_thread()

            # Save the new thread in the database
            thread = await save_thread(db, str(sender_id), str(owner_id), assistant_id, thread_id, platform)
            logger.info(f"New thread created and saved for sender_id={str(sender_id)}, owner_id={str(owner_id)}.")
        else:
            # Step 4: Reuse the existing thread
            assistant_manager.set_thread(thread.thread_id)
            logger.info(f"Reusing existing thread with ID={thread.thread_id} for sender_id={str(sender_id)}.")

        # Step 5: Add the incoming message to the thread
        assistant_manager.add_message_to_thread(role="user", content=message)
        logger.info(f"Message added to thread ID={assistant_manager.thread_id}: {message}")

        # Step 6: Run the assistant and wait for completion
        assistant_manager.run_assistant(instructions="Generate a response based on the conversation context.")
        response = assistant_manager.wait_for_completion()

        return {
            "thread_id": assistant_manager.thread_id,
            "response": response
        }
    except Exception as e:
        logger.error(f"Error in handle_incoming_message: {e}")
        raise



def create_assistant_in_openai(name: str, instructions: str, creativity: float) -> str:
    """
    Создаёт ассистента в OpenAI через AssistantManager и возвращает assistant_id.
    Параметр 'creativity' можно где-то учесть, например, менять model или instructions.
    """
    manager = AssistantManager(model="gpt-3.5-turbo")  # или другой
    assistant_id = manager.create_assistant(
        name=name,
        instructions=instructions,
        tools=[]  # передайте, если нужны
    )
    return assistant_id
