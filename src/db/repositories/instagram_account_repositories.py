from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.db.models.instagram_models import InstagramAccount


async def create_instagram_account(db: AsyncSession, username, user_id, access_token):
    instagram_account = InstagramAccount(
        username=username,
        user_id=user_id,
        access_token=access_token,
    )
    db.add(instagram_account)
    await db.commit()

async def get_instagram_account(db: AsyncSession, user_id):
    statement = select(InstagramAccount).where(InstagramAccount.user_id == user_id)
    result = await db.execute(statement)
    user = result.scalars().first()
    return user