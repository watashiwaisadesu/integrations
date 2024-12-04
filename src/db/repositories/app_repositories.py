from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from src.db.models.instagram_models import App

class InstagramCredentials:
    def __init__(self, app):
        self.id = app.id
        self.inst_app_id = app.inst_app_id
        self.inst_app_secret = app.inst_app_secret
        self.webhook_callback_url = app.webhook_callback_url
        self.webhook_verify_token = app.webhook_verify_token
        self.handle_code_url = app.handle_code_url
        self.embed_url = app.embed_url

    @property
    def credentials(self):
        """Return only app_id and app_secret."""
        return self.inst_app_id, self.inst_app_secret

    def all_details(self):
        """Return all available details."""
        return {
            "id": self.id,
            "inst_app_id": self.inst_app_id,
            "inst_app_secret": self.inst_app_secret,
            "webhook_callback_url": self.webhook_callback_url,
            "webhook_verify_token": self.webhook_verify_token,
            "handle_code_url": self.handle_code_url,
            "embed_url": self.embed_url,
        }

async def get_instagram_credentials(db: AsyncSession, return_type="all"):
    """
    Fetch Instagram credentials with flexible return types.

    :param db: AsyncSession object
    :param return_type: "all" for all details, "credentials" for app_id and app_secret only
    :return: InstagramCredentials instance or subset of details
    """
    app = await db.get(App, 1)  # Fetch the single row with ID = 1
    if app is None:
        return None

    credentials = InstagramCredentials(app)

    if return_type == "credentials":
        return credentials.credentials
    elif return_type == "all":
        return credentials.all_details()
    else:
        raise ValueError(f"Unknown return_type: {return_type}")

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


def set_app_details(db: Session, app_id: str, app_secret: str, embed_url: str, handle_code_url: str, webhook_verify_token: str, webhook_callback_url: str):
    app = db.get(App, 1)
    if app is None:
        app = App(
            inst_app_id=app_id,
            inst_app_secret=app_secret,
            embed_url=embed_url,
            handle_code_url=handle_code_url,
            webhook_verify_token=webhook_verify_token,
            webhook_callback_url=webhook_callback_url,
        )
        db.add(app)
    else:
        app.inst_app_id = app_id
        app.inst_app_secret = app_secret
        app.embed_url = embed_url
        app.handle_code_url = handle_code_url
        app.webhook_verify_token = webhook_verify_token
        app.webhook_callback_url = webhook_callback_url

    print("webhook details set to db")
    db.commit()