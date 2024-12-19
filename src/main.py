from fastapi import FastAPI

from src.instagram_api.routes import instagram_api_router
from src.core.middleware import register_middleware
from src.whatsapp_api.routes import whatsapp_api_router
from src.telegram_api.routes import telegram_api_router
from src.external_service.routes import external_service_api_router
# from src.utils.error_handler import register_all_errors

version = "v1"

description = """
Integrations Service using
Instagram Graph API, Telethon, GreenAPI
"""

version_prefix = f"/{version}"

app = FastAPI(
    title="Integrations",
    description=description,
    version=version,
    license_info={"name": "MIT License","url":"https://opensource.org/licenses/MIT"},
    contact={
        "name": "isaog",
        "url": "https://github.com/watashiwaisadesu/integrations",
        "email": "islambek040508@gmail.com",
    },
    docs_url=f"{version_prefix}/docs",
)

register_middleware(app)
# register_all_errors(app)

app.include_router(external_service_api_router, prefix=f"{version_prefix}/external_service", tags=["External Service"])
app.include_router(instagram_api_router, prefix=f"{version_prefix}/instagram", tags=["InstagramAPI"])
app.include_router(telegram_api_router, prefix=f"{version_prefix}/telegram", tags=["TelegramAPI"])
app.include_router(whatsapp_api_router, prefix=f"{version_prefix}/whatsapp", tags=["WhatsappAPI"])

