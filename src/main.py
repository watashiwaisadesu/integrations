from fastapi import FastAPI

from src.instagram_api.routes import instagram_api_router
from src.webhook_config.routes import webhook_setup_router
from src.core.middleware import register_middleware
# from src.utils.error_handler import register_all_errors

version = "v1"

description = """
Integrations Service using
selenium setup webhook and get necessary details at 
https://developers.facebook.com 
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

app.include_router(instagram_api_router, prefix=f"{version_prefix}/instagram", tags=["InstagramAPI"])
app.include_router(webhook_setup_router, prefix=f"{version_prefix}/webhook", tags=["WebhookSetup"])
