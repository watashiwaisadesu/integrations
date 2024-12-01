from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from src.db.models.instagram_models import App


async def get_instagram_credentials(db: AsyncSession):
    app = await db.get(App, 1)  # Fetch the single row with ID = 1
    if app is None:
        return None, None
    return app.inst_app_id, app.inst_app_secret


async def set_instagram_credentials(db: AsyncSession, app_id: str, app_secret: str):
    app = await db.get(App, 1)
    if app is None:
        app = App(inst_app_id=app_id, inst_app_secret=app_secret)
        db.add(app)
    else:
        app.inst_app_id = app_id
        app.inst_app_secret = app_secret
    await db.commit()


async def get_webhook_details(db: AsyncSession):
    app = await db.get(App, 1)  # Fetch the single row with ID = 1
    if app is None:
        return None, None
    return app.webhook_verify_token, app.webhook_callback_url


def set_webhook_details(db: Session, webhook_verify_token: str, webhook_callback_url: str):
    app = db.get(App, 1)
    if app is None:
        app = App(webhook_verify_token=webhook_verify_token, webhook_callback_url=webhook_callback_url)
        db.add(app)
    else:
        app.webhook_verify_token = webhook_verify_token
        app.webhook_callback_url = webhook_callback_url
    print("webhook details set to db")
    db.commit()