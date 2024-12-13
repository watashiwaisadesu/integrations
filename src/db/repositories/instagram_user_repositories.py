from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.db.models.instagram_models import InstagramUser


async def create_instagram_account(db: AsyncSession, username, user_id, access_token):
    user = await get_instagram_account(db, user_id)
    if user is None:
        instagram_account = InstagramUser(
            username=username,
            user_id=user_id,
            access_token=access_token,
        )
        db.add(instagram_account)
    else:
        user.access_token = access_token
    await db.commit()


async def get_instagram_account(db: AsyncSession, user_id):
    statement = select(InstagramUser).where(InstagramUser.user_id == user_id)
    result = await db.execute(statement)
    user = result.scalars().first()
    return user