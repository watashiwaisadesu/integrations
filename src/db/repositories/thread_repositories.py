# src/db/repositories/thread_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.db.models.openai_models import Thread
import uuid


async def get_thread(db: AsyncSession, sender_id: str, owner_id: str, platform: str):
    """
    Fetch an existing thread by sender_id and owner_id.
    """
    statement = select(Thread).where(Thread.sender_id == sender_id, Thread.owner_id == owner_id, Thread.platform == platform)
    result = await db.execute(statement)
    return result.scalars().first()


async def save_thread(db: AsyncSession, sender_id: str, owner_id: str, assistant_id: str, thread_id: str, platform: str):
    """
    Save a new thread to the database.
    """
    new_thread = Thread(
        thread_id=thread_id,
        sender_id=sender_id,
        owner_id=owner_id,
        assistant_id=assistant_id,
        platform=platform
    )
    db.add(new_thread)
    await db.commit()
    return new_thread
