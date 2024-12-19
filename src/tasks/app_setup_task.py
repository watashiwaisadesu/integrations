import time
from pydantic import EmailStr

from src.db.repositories.instagram_app_repositories import set_app_details, set_app_verify_token
from src.instagram_api.automation.auth import perform_login
from src.instagram_api.automation.navigation import (
    navigate_to_login_page,
    navigate_to_my_apps,
    locate_app_href,
    navigate_to_webhook_service,
    navigate_to_instagramapi_service
)
from src.instagram_api.automation.webhook_manager import configure_webhook_product, configure_instagram_api_product
from src.core.driver_setup import initialize_webdriver_headless
from src.core.celery_setup import celery
from src.core.database_setup import get_sync_db


@celery.task
def app_setup_task(email: EmailStr, password: str, verify_token: str, base_url: str, app_name: str):
    session = get_sync_db()
    webhook_callback_url = base_url + "v1/instagram/webhook"
    handle_code_url = base_url + "v1/instagram/handle_code"
    set_app_verify_token(session, verify_token)
    time.sleep(1)
    driver = initialize_webdriver_headless()
    try:
        navigate_to_login_page(driver)
        perform_login(driver, email, password)
        navigate_to_my_apps(driver)
        # Locate the app link
        app_href = locate_app_href(driver, app_name)

        navigate_to_webhook_service(driver, app_href)
        configure_webhook_product(driver, verify_token, webhook_callback_url)

        navigate_to_instagramapi_service(driver, app_href)
        inst_app_id, inst_app_secret, embed_url = configure_instagram_api_product(driver, verify_token, webhook_callback_url, handle_code_url, session)
        set_app_details(db=session, app_id=inst_app_id, app_secret=inst_app_secret, handle_code_url=handle_code_url,
                      embed_url=embed_url,  webhook_verify_token=verify_token, webhook_callback_url=webhook_callback_url)
        print("App details setup completed successfully.")
        return {"status": "success", "message": "Webhook setup completed successfully.","embed_url": embed_url}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {"status": "failure", "message": str(e)}
    finally:
        driver.quit()
