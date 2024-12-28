import time
import logging

logger = logging.getLogger(__name__)

def navigate_to_login_page(driver):
    driver.get('https://console.green-api.com/auth')
    logger.info(f"Navigated to login page (GreenAPI)")
    time.sleep(1)

def navigate_to_create_instance(driver):
    driver.get('https://console.green-api.com/instanceList/tariff/BUSINESS_KAZ/month1?quantityInstances=1')

def navigate_to_instance_page(driver, id_instance):
    driver.get(f'https://console.green-api.com/instanceList/{id_instance}')
    logger.info(f"Navigated to 'https://console.green-api.com/instanceList/{id_instance}")

def navigate_to_payment_url(driver, payment_url):
    driver.get(payment_url)

