from src.core.celery_setup import celery
from src.core.database_setup import get_sync_db
from src.core.driver_setup import initialize_webdriver_headless, initialize_webdriver_visible
from src.db.repositories.external_service_app_repositories import get_app_external_service_base_url_sync
from src.db.repositories.whatsapp_user_repositories import create_or_update_whatsapp_user
from src.external_service.service import create_bot_request_sync
from src.whatsapp_api.automation.auth import perform_login
from src.whatsapp_api.automation.service import (
    get_paid_order_instance_id,
    get_instance_credentials,
    set_settings,
    get_qr_code
)
from src.whatsapp_api.automation.navigation import (
    navigate_to_login_page,
    navigate_to_instance_page, navigate_to_payment_url
)


@celery.task
def create_instance_task(email: str, password: str,callback_url: str):
    session = get_sync_db()
    driver_headless = initialize_webdriver_headless()
    driver_visible = None  # Initialize driver_visible as None
    target_result_url = "https://checkout.paymtech.kz/complete/bcc"
    try:
        navigate_to_login_page(driver_headless)
        perform_login(driver_headless, email, password)

        # Perform the Pay process and fetch the response
        # response = get_payment_url(driver_headless)
        # if isinstance(response, dict):  # Ensure response is a dictionary
        #     response_data = response
        # else:
        #     response_data = response.json()

        # payment_url = response_data.get('data', {}).get('paymentURL')
        # Initialize visible driver
        # driver_visible = initialize_webdriver_visible()
        #
        # # Perform further actions in visible mode
        # print("Switched to visible browser.")
        #
        # navigate_to_payment_url(driver_visible, payment_url)
        # print("Payment URL loaded in visible browser.")
        #
        # WebDriverWait(driver_visible, 1800).until(
        #     lambda d: target_result_url in d.current_url
        # )
        # print("Reached target result URL:", driver_visible.current_url)
        # driver_visible.quit()
        # order_id = payment_url.split('/')[-1]
        # print(order_id)
        # time.sleep(5)
        order_id = '90204867127858778'

        id_instance = get_paid_order_instance_id(driver_headless, order_id)
        if not id_instance:
            raise Exception("Couldn't find id_instance")
        # id_instance = '7103164152'
        navigate_to_instance_page(driver_headless, id_instance)
        print(id_instance)
        api_url, media_url, api_token = get_instance_credentials(driver_headless)
        external_service_base_url = get_app_external_service_base_url_sync(session)
        bot_url = create_bot_request_sync(id_instance, external_service_base_url, True)
        if not bot_url:
            return {"error": "Failed to create bot."}, 500
        set_settings(api_url,id_instance,api_token,callback_url)
        create_or_update_whatsapp_user(session,api_url,id_instance,api_token,bot_url, order_id)
        return get_qr_code(api_url,id_instance,api_token)
    except Exception as e:
        # Cleanup headless driver
        if driver_headless:
            driver_headless.quit()

        # Cleanup visible driver if initialized
        if driver_visible:
            driver_visible.quit()

        raise e





