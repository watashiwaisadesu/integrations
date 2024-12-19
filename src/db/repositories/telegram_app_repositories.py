import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.telegram_models import TelegramApp

async def set_telegram_app(api_id: str, api_hash: str, db: AsyncSession) -> TelegramApp:
    """
    Ensure only one Telegram app exists. If not found, create it. Otherwise, update.
    """
    app = await db.get(TelegramApp, 1)  # Assuming the single app always has ID = 1
    if app is None:
        app = TelegramApp(api_id=api_id, api_hash=api_hash)
        db.add(app)
    else:
        app.api_id = api_id
        app.api_hash = api_hash
    await db.commit()
    return app


async def get_current_app(db: AsyncSession) -> TelegramApp:
    """
    Retrieve the current TelegramApp (assuming only one).
    """
    app = await db.get(TelegramApp, 1)
    if app is None:
        raise ValueError("Telegram app is not set. Use /set-app to configure.")
    return app
