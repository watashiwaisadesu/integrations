import logging
import json
import time
import requests
from selenium.webdriver.common.by import By
from src.utils.automation_tools import wait_for_element

# Import your custom exceptions
from src.utils.errors_handler import InternalServerError, ExternalServiceError

logger = logging.getLogger(__name__)

def fetch_authorization_token(driver):
    """
    Attempts to locate an Authorization header (Bearer token) in driver's captured requests.
    """
    logger.debug("Attempting to fetch authorization token from captured driver requests.")
    try:
        for req in driver.requests:
            auth_header = req.headers.get("Authorization")
            if auth_header and "Bearer" in auth_header:
                logger.info(f"Captured Authorization Token: {auth_header}")
                return auth_header
        logger.warning("No authorization token found among driver requests.")
        return None
    except Exception as e:
        logger.error(f"Error fetching authorization token: {e}")
        # Raise a general internal error if something goes unexpectedly wrong
        raise InternalServerError("Failed to fetch authorization token.") from e


def get_payment_url(driver):
    """
    Retrieve the payment URL by making a POST request with the captured auth token.
    """
    logger.debug("Starting get_payment_url process.")
    try:
        token = fetch_authorization_token(driver)
        if not token:
            logger.error("Authorization token not found!")
            raise InternalServerError("Authorization token not found!")

        cookies = {cookie['name']: cookie['value'] for cookie in driver.get_cookies()}
        print(cookies)

        headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Origin': 'https://console.green-api.com',
            'Referer': 'https://console.green-api.com/instanceList/tariff/BUSINESS_KAZ/month1?quantityInstances=1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)',
            'authorization': token,
            'x-ga-method': 'user.instance.createInstances',
            'x-ga-user-id': cookies.get('idUser'),
            'x-ga-user-token': cookies.get('apiTokenUser'),
        }

        json_data = {
            'tariff': 'BUSINESS_KAZ',
            'period': 'month1',
            'payment': 'bcc_kzt',
            'quantity': 1,
            'idCompany': '',
        }

        logger.debug("Sending POST request to retrieve payment URL.")
        response = requests.post(
            'https://console.green-api.com/api/v1/',
            cookies=cookies,
            headers=headers,
            json=json_data
        )

        # Optionally check for HTTP errors
        try:
            response.raise_for_status()
        except requests.HTTPError as http_err:
            logger.error(f"HTTP error in get_payment_url: {http_err} - {response.text}")
            raise ExternalServiceError("Failed to communicate with Green API for payment URL.") from http_err

        logger.info(f"Payment URL Response: {response.text}")
        return response.json()

    except ExternalServiceError:
        raise  # Re-raise to preserve status code handling
    except requests.RequestException as req_err:
        logger.error(f"Request error in get_payment_url: {req_err}")
        raise ExternalServiceError("Failed to communicate with Green API for payment URL.") from req_err
    except Exception as e:
        logger.error(f"Unexpected error in get_payment_url: {e}")
        raise InternalServerError("Unexpected error retrieving payment URL.") from e


def get_paid_order_instance_id(driver, order_id):
    """
    Retrieve the instance ID associated with a specified order if that order is paid and confirmed.
    """
    logger.debug(f"Fetching paid order instance for order_id={order_id}")
    try:
        token = fetch_authorization_token(driver)
        if not token:
            logger.error("No authorization token found while fetching paid order.")
            raise InternalServerError("Authorization token not found!")

        cookies = {cookie['name']: cookie['value'] for cookie in driver.get_cookies()}
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': 'https://console.green-api.com',
            'Referer': f'https://console.green-api.com/instanceList/tariff/result?order_id={order_id}',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)',
            'authorization': token,
            'x-ga-method': 'user.order.getList',
            'x-ga-user-id': cookies.get('idUser'),
            'x-ga-user-token': cookies.get('apiTokenUser'),
        }

        response = requests.post('https://console.green-api.com/api/v1/', cookies=cookies, headers=headers)
        response.raise_for_status()

        response_data = response.json()
        print(response)

        data_list = response_data.get('data', [])
        matching_entry = None

        for entry in data_list:
            payment_url = entry.get('paymentURL', '')
            if payment_url.endswith(order_id):
                matching_entry = entry
                break

        if matching_entry:
            print("Found matching order entry:")
            print(matching_entry)
            if matching_entry.get('paymentStatus') == 'paid' and matching_entry.get('isConfirmed') is True:
                print("Order is fully paid and confirmed.")
                instances = matching_entry.get('instances', [])
                if instances:
                    return instances[0]
                else:
                    print("No instances found in the matching order.")
                    return None
            else:
                print("Order is not fully paid or still pending confirmation.")
                return None
        else:
            print("No order found with the specified order_id.")
            return None

    except requests.HTTPError as http_err:
        logger.error(f"HTTP error in get_paid_order_instance_id: {http_err}")
        raise ExternalServiceError("Failed to communicate with Green API for order details.") from http_err
    except requests.RequestException as req_err:
        logger.error(f"Request error in get_paid_order_instance_id: {req_err}")
        raise ExternalServiceError("Request issue fetching order instance.") from req_err
    except Exception as e:
        logger.error(f"Unexpected error in get_paid_order_instance_id: {e}")
        raise InternalServerError("Error fetching paid order instance details.") from e


def get_instance_credentials(driver):
    """
    Retrieve the instance credentials (apiURL, mediaURL, apiToken) from the page elements.
    """
    logger.debug("Starting get_instance_credentials.")
    try:
        # XPaths remain unchanged
        api_url_xpath = '//main//table/tbody/tr[1]/td/span'
        media_url_xpath = '//main//table/tbody/tr[2]/td/span'
        view_api_token_xpath = '//main//table/tbody/tr[4]/td/span/div/div[2]/div/div[2]/div/div/span'
        api_token_xpath = '//main//table/tbody/tr[4]/td/span/div/div[1]'

        api_url = wait_for_element(driver, By.XPATH, api_url_xpath, condition="visible")
        api_url_text = api_url.text
        print(api_url_text)

        media_url = wait_for_element(driver, By.XPATH, media_url_xpath)
        media_url_text = media_url.text
        print(media_url_text)

        view_api_token = wait_for_element(driver, By.XPATH, view_api_token_xpath)
        view_api_token.click()

        api_token = wait_for_element(driver, By.XPATH, api_token_xpath)
        api_token_text = api_token.text
        print(f"apiToken: {api_token_text}")

        return api_url_text, media_url_text, api_token_text

    except Exception as e:
        logger.error(f"Error in get_instance_credentials: {e}")
        raise InternalServerError("Failed to retrieve instance credentials.") from e


def transfer_cookies(source_driver, target_driver):
    """
    Transfer all cookies from source_driver to target_driver,
    then refresh to apply them.
    """
    logger.debug("Starting transfer_cookies.")
    try:
        cookies = source_driver.get_cookies()
        target_driver.get(source_driver.current_url)
        for cookie in cookies:
            target_driver.add_cookie(cookie)
        target_driver.refresh()
        logger.info("Cookies transferred and page refreshed.")
    except Exception as e:
        logger.error(f"Error transferring cookies: {e}")
        raise InternalServerError("Cookie transfer failed.") from e


def set_settings(api_url: str, id_instance: str, api_token: str, callback_url: str):
    """
    Configure Green API instance settings with the provided callback_url and other parameters.
    """
    logger.debug("Starting set_settings.")
    url = f"{api_url}/waInstance{id_instance}/setSettings/{api_token}"
    payload = {
        "webhookUrl": callback_url,
        "delaySendMessagesMilliseconds": 1000,
        "markIncomingMessagesReaded": "no",
        "outgoingWebhook": "yes",
        "stateWebhook": "yes",
        "incomingWebhook": "yes",
        "deviceWebhook": "no"
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        logger.info(f"set_settings response: {response.text.encode('utf8')}")
    except requests.HTTPError as http_err:
        logger.error(f"HTTP error in set_settings: {http_err}")
        raise ExternalServiceError("Failed to set instance settings.") from http_err
    except requests.RequestException as req_err:
        logger.error(f"Request error in set_settings: {req_err}")
        raise ExternalServiceError("Connection issue while setting instance settings.") from req_err
    except Exception as e:
        logger.error(f"Unexpected error in set_settings: {e}")
        raise InternalServerError("Unexpected error setting instance settings.") from e


def get_qr_code(api_url: str, id_instance: str, api_token: str):
    """
    Retrieve a QR code from the Green API instance.
    """
    logger.debug("Starting get_qr_code.")
    url = f"{api_url}/waInstance{id_instance}/qr/{api_token}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = json.loads(response.text)
        print(data['message'])
        return data['message']
    except requests.HTTPError as http_err:
        logger.error(f"HTTP error in get_qr_code: {http_err}")
        raise ExternalServiceError("Failed to fetch QR code from Green API.") from http_err
    except requests.RequestException as req_err:
        logger.error(f"Request error in get_qr_code: {req_err}")
        raise ExternalServiceError("Network issue fetching QR code.") from req_err
    except Exception as e:
        logger.error(f"Unexpected error in get_qr_code: {e}")
        raise InternalServerError("Error retrieving QR code.") from e
