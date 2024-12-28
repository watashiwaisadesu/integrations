import time
from selenium.webdriver.support.ui import WebDriverWait
import logging

from src.core.celery_setup import celery
from src.core.database_setup import get_sync_db
from src.core.driver_setup import initialize_webdriver_headless, initialize_webdriver_visible
from src.db.repositories.whatsapp_user_repositories import create_or_update_whatsapp_user
from src.messengers.whatsapp_api.automation.auth import perform_login
from src.messengers.whatsapp_api.automation.service import (
    get_paid_order_instance_id,
    get_instance_credentials,
    set_settings,
    get_qr_code,
    get_payment_url
)
from src.messengers.whatsapp_api.automation.navigation import (
    navigate_to_login_page,
    navigate_to_instance_page, navigate_to_payment_url
)

logger = logging.getLogger(__name__)


@celery.task
def create_instance_task(email: str, password: str, callback_url: str):
    """
    Celery task to create a new WhatsApp instance, handle the payment process,
    configure instance settings, and retrieve a QR code.
    """
    logger.info("Starting create_instance_task")
    db_sync = get_sync_db()
    driver_headless = initialize_webdriver_headless()
    driver_visible = None  # Will be initialized later
    target_result_url = "https://checkout.paymtech.kz/complete/bcc"
    home_url = "https://console.green-api.com/auth"

    try:
        logger.debug("Navigating to login page on headless driver.")
        navigate_to_login_page(driver_headless)

        logger.debug("Performing login with provided credentials.")
        perform_login(driver_headless, email, password)

        logger.debug("Fetching payment URL in headless mode.")
        response = get_payment_url(driver_headless)
        if isinstance(response, dict):
            response_data = response
        else:
            response_data = response.json()

        payment_url = response_data.get('data', {}).get('paymentURL')
        logger.debug(f"Payment URL received: {payment_url}")

        # Switch to a visible browser for payment
        logger.debug("Initializing visible browser for payment flow.")
        driver_visible = initialize_webdriver_visible()
        logger.info("Switched to visible browser.")

        navigate_to_payment_url(driver_visible, payment_url)
        logger.info("Payment URL loaded in visible browser.")

        logger.debug("Waiting up to 1800s for either target_result_url or home_url.")
        WebDriverWait(driver_visible, 1800).until(
            lambda d: target_result_url in d.current_url or home_url in d.current_url
        )
        logger.info(f"Reached target result URL or home page: {driver_visible.current_url}")
        driver_visible.quit()

        order_id = payment_url.split('/')[-1]
        logger.debug(f"Extracted order_id: {order_id}")

        time.sleep(5)  # Pause to ensure order is processed

        logger.debug("Attempting to fetch paid order instance ID.")
        # id_instance = get_paid_order_instance_id(driver_headless, order_id)
        id_instance = '7103164152'
        if not id_instance:
            raise Exception("Couldn't find id_instance")

        logger.debug(f"Navigating to instance page with id_instance={id_instance}.")
        navigate_to_instance_page(driver_headless, id_instance)

        logger.debug("Retrieving instance credentials.")
        api_url, media_url, api_token = get_instance_credentials(driver_headless)

        logger.debug("Setting instance configuration.")
        set_settings(api_url, id_instance, api_token, callback_url)

        logger.debug("Creating or updating WhatsApp user record in DB.")
        create_or_update_whatsapp_user(db_sync, api_url, id_instance, api_token, callback_url, order_id, None)

        logger.debug("Retrieving QR code to complete setup.")
        qr_code = get_qr_code(api_url, id_instance, api_token)
        logger.debug(f"QR code retrieved: {qr_code}")

        logger.info("create_instance_task completed successfully.")
        return qr_code, api_url, id_instance, api_token

    except Exception as e:
        logger.error(f"Error in create_instance_task: {e}")

        # Cleanup headless driver
        if driver_headless:
            driver_headless.quit()
            logger.debug("Closed headless driver due to exception.")

        # Cleanup visible driver
        if driver_visible:
            driver_visible.quit()
            logger.debug("Closed visible driver due to exception.")

        # If you want to raise a custom exception, e.g.:
        # raise InternalServerError("Failed to create WhatsApp instance.") from e
        # Otherwise, simply re-raise:
        raise e





