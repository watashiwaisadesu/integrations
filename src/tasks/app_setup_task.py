import logging
import time
from pydantic import EmailStr

from src.db.repositories.instagram_app_repositories import set_app_details, set_app_verify_token
from src.messengers.instagram_api.automation.auth import perform_login
from src.messengers.instagram_api.automation.navigation import (
    navigate_to_login_page,
    navigate_to_my_apps,
    locate_app_href,
    navigate_to_webhook_service,
    navigate_to_instagramapi_service
)
from src.messengers.instagram_api.automation.webhook_manager import configure_webhook_product, configure_instagram_api_product
from src.core.driver_setup import initialize_webdriver_headless
from src.core.celery_setup import celery
from src.core.database_setup import get_sync_db

# Import any custom exceptions if desired, e.g.:
# from src.utils.errors_handler import InternalServerError

logger = logging.getLogger(__name__)


@celery.task
def app_setup_task(email: EmailStr, password: str, verify_token: str, base_url: str, app_name: str):
    """
    Celery task that logs into the Facebook developer console, configures the webhook,
    and sets up the Instagram API product for the specified app.
    """
    logger.info(f"Starting app_setup_task for app_name={app_name} with user={email}")

    session = get_sync_db()
    webhook_callback_url = base_url + "v1/instagram/webhook"
    handle_code_url = base_url + "v1/instagram/handle_code"

    logger.debug("Setting up app verify token in DB.")
    set_app_verify_token(session, verify_token)
    time.sleep(1)

    driver = initialize_webdriver_headless()
    logger.debug("Initialized headless driver.")

    try:
        logger.debug("Navigating to login page.")
        navigate_to_login_page(driver)

        logger.debug("Performing login with provided credentials.")
        perform_login(driver, email, password)

        logger.debug("Navigating to 'My Apps' in the developer console.")
        navigate_to_my_apps(driver)

        logger.debug(f"Locating app href for {app_name}.")
        app_href = locate_app_href(driver, app_name)

        logger.debug("Navigating to webhook service.")
        navigate_to_webhook_service(driver, app_href)

        logger.debug("Configuring webhook product.")
        configure_webhook_product(driver, verify_token, webhook_callback_url)

        logger.debug("Navigating to Instagram API service.")
        navigate_to_instagramapi_service(driver, app_href)

        logger.debug("Configuring Instagram API product.")
        inst_app_id, inst_app_secret, embed_url = configure_instagram_api_product(
            driver,
            verify_token,
            webhook_callback_url,
            handle_code_url,
            session
        )

        logger.debug("Storing app details in DB.")
        set_app_details(
            db=session,
            app_id=inst_app_id,
            app_secret=inst_app_secret,
            handle_code_url=handle_code_url,
            embed_url=embed_url,
            webhook_verify_token=verify_token,
            webhook_callback_url=webhook_callback_url
        )

        print("App details setup completed successfully.")
        logger.info("Webhook setup completed successfully.")

        return {
            "status": "success",
            "message": "Webhook setup completed successfully.",
            "embed_url": embed_url
        }

    except Exception as e:
        logger.error(f"Error in app_setup_task: {e}")
        print(f"An error occurred: {e}")
        return {
            "status": "failure",
            "message": str(e)
        }

    finally:
        logger.debug("Quitting driver.")
        driver.quit()
