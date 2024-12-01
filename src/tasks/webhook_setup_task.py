from celery import Celery
from pydantic import EmailStr

from src.webhook_config.cookies_utils import load_cookies_from_db, save_cookies_to_db
from src.db.repositories.app_repositories import set_webhook_details
from src.webhook_config.auth import perform_login
from src.webhook_config.navigation import navigate_to_my_apps, locate_neuro_employees
from src.webhook_config.webhook_manager import configure_webhook_product, configure_webhook_for_instagram_api_product
from src.webhook_config.webdriver_utils import initialize_webdriver
from src.core.config import SYNC_DATABASE_URL
from src.core.celery_setup import celery
from src.core.database_setup import get_sync_db


@celery.task
def webhook_setup_task(email: EmailStr, password: str, verify_token: str, callback_url: str, app_name: str):
    driver = initialize_webdriver()
    session = get_sync_db()
    try:
        # Handle cookies
        if load_cookies_from_db(session, email, driver):
            print("Cookies loaded successfully from the database.")
            driver.refresh()
        else:
            print("Cookies not found in the database, performing login.")
            perform_login(driver, email, password)
            save_cookies_to_db(session, email, driver)
            print("Cookies saved to the database successfully.")

        driver.get('https://developers.facebook.com/')
        set_webhook_details(session, verify_token, callback_url)
        navigate_to_my_apps(driver)
        neuro_employees_href = locate_neuro_employees(driver, app_name)

        # Perform webhook updates
        configure_webhook_product(driver, neuro_employees_href, verify_token, callback_url)

        # Additional interactions
        configure_webhook_for_instagram_api_product(driver, neuro_employees_href, verify_token, callback_url)
        print("Webhook setup completed successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()
