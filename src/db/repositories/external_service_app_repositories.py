from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from src.db.models.external_service_models import ExternalServiceApp

async def get_app_external_service_base_url(db: AsyncSession):
    app = await db.get(ExternalServiceApp, 1)
    if app:
        return app.external_service_base_url
    return None

def get_app_external_service_base_url_sync(db: Session):
    app = db.get(ExternalServiceApp, 1)
    if app:
        return app.external_service_base_url
    return None

async def set_app_external_service_base_url(db: AsyncSession, external_service_base_url: str):
    app = await db.get(ExternalServiceApp, 1)
    if app is None:
        app = ExternalServiceApp(
            external_service_base_url=external_service_base_url
        )
        db.add(app)
    else:
        app.external_service_base_url = external_service_base_url

    print("external_service_base_url setup completed")
    await db.commit()
