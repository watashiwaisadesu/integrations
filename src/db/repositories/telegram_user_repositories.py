import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models.telegram_models import TelegramUser

async def add_or_update_telegram_user(phone_number: str, db: AsyncSession, **kwargs) -> TelegramUser:
    """
    Add or update a TelegramUser record. If the user doesn't exist, create them.
    Update the provided fields from kwargs.
    """
    result = await db.execute(
        sa.select(TelegramUser).where(TelegramUser.phone_number == phone_number)
    )
    user = result.scalars().first()

    if user is None:
        user = TelegramUser(phone_number=phone_number)
        db.add(user)
        await db.flush()  # ensure user.id is generated

    for key, value in kwargs.items():
        setattr(user, key, value)

    await db.commit()
    return user

async def get_user_by_phone(phone_number: str, db: AsyncSession) -> TelegramUser:
    result = await db.execute(
        sa.select(TelegramUser).where(TelegramUser.phone_number == phone_number)
    )
    return result.scalars().first()

async def get_user_by_username(username: str, db: AsyncSession) -> TelegramUser:
    result = await db.execute(
        sa.select(TelegramUser).where(TelegramUser.username == username)
    )
    return result.scalars().first()