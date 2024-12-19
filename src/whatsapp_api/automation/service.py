import json
import time

import requests
from selenium.webdriver.common.by import By

from src.utils.automation_tools import wait_for_element



def fetch_authorization_token(driver):
    for request in driver.requests:
        if request.headers.get("Authorization") and "Bearer" in request.headers.get("Authorization"):
            token = request.headers.get("Authorization")
            print(f"Captured Authorization Token: {token}")
            return token
    return None


def get_payment_url(driver):
    token = fetch_authorization_token(driver)
    if not token:
        raise Exception("Authorization token not found!")
    cookies = {cookie['name']: cookie['value'] for cookie in driver.get_cookies()}
    print(cookies)
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Origin': 'https://console.green-api.com',
        'Referer': 'https://console.green-api.com/instanceList/tariff/BUSINESS_KAZ/month1?quantityInstances=1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'authorization': token,
        'x-ga-method': 'user.instance.createInstances',
        'x-ga-user-id': cookies.get('idUser'),  # Replace with appropriate cookie or dynamic value
        'x-ga-user-token': cookies.get('apiTokenUser'),  # Replace with appropriate cookie or dynamic value
    }

    # JSON data for the request
    json_data = {
        'tariff': 'BUSINESS_KAZ',
        'period': 'month1',
        'payment': 'bcc_kzt',
        'quantity': 1,
        'idCompany': '',
    }

    # Make the POST request
    response = requests.post(
        'https://console.green-api.com/api/v1/',
        cookies=cookies,
        headers=headers,
        json=json_data
    )
    return response.json()


def get_paid_order_instance_id(driver, order_id):
    """
    Retrieve the instance ID associated with a specified order if that order is paid and confirmed.

    :param driver: The Selenium WebDriver instance (with user logged in).
    :param order_id: The order identifier we want to look up.
    :return: The 'idInstance' value if the order is paid and confirmed, or None otherwise.
    """
    token = fetch_authorization_token(driver)
    cookies = {cookie['name']: cookie['value'] for cookie in driver.get_cookies()}

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Origin': 'https://console.green-api.com',
        'Referer': f'https://console.green-api.com/instanceList/tariff/result?order_id={order_id}',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
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

    # Find the order entry whose paymentURL ends with the given order_id
    for entry in data_list:
        payment_url = entry.get('paymentURL', '')
        if payment_url.endswith(order_id):
            matching_entry = entry
            break

    if matching_entry:
        print("Found matching order entry:")
        print(matching_entry)
        # Check if the order is fully paid and confirmed
        if matching_entry.get('paymentStatus') == 'paid' and matching_entry.get('isConfirmed') is True:
            print("Order is fully paid and confirmed.")
            instances = matching_entry.get('instances', [])
            # Return the first instance safely
            if instances:
                return instances[0]
            else:
                print("No instances found in the matching order.")
        else:
            print("Order is not fully paid or still pending confirmation.")
            return None
    else:
        print("No order found with the specified order_id.")
        return None


def get_instance_credentials(driver):
    # 1. Get apiURL '/main/div/div[5]/div[1]/div/div[1]/div/div/table/tbody/tr[1]/td/span
    api_url_xpath = '//main//table/tbody/tr[1]/td/span'

    api_url = wait_for_element(driver, By.XPATH, api_url_xpath, condition="visible")
    api_url_text = api_url.text
    print(api_url_text)

    # 2. Get mediaURL
    media_url_xpath = '//main//table/tbody/tr[2]/td/span'
    media_url = wait_for_element(driver, By.XPATH, media_url_xpath)
    media_url_text = media_url.text
    print(media_url_text)

    # Click on the view button to reveal API Token
    view_api_token_xpath = '//main//table/tbody/tr[4]/td/span/div/div[2]/div/div[2]/div/div/span'
    view_api_token = wait_for_element(driver, By.XPATH, view_api_token_xpath)
    view_api_token.click()

    # 3. Get apiToken
    api_token_xpath = '//main//table/tbody/tr[4]/td/span/div/div[1]'
    api_token = wait_for_element(driver, By.XPATH, api_token_xpath)
    api_token_text = api_token.text
    print(f"apiToken: {api_token_text}")

    return api_url_text, media_url_text, api_token_text


def transfer_cookies(source_driver, target_driver):
    cookies = source_driver.get_cookies()
    target_driver.get(source_driver.current_url)
    for cookie in cookies:
        target_driver.add_cookie(cookie)
    target_driver.refresh()


def set_settings(api_url: str,id_instance: str,api_token: str, callback_url: str):
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

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(url, json=payload)

    print(response.text.encode('utf8'))


def get_qr_code(api_url: str,id_instance: str,api_token: str):
    url = f"{api_url}/waInstance{id_instance}/qr/{api_token}"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    # print(f"QR code: {response.text.encode('utf8')}")
    data = json.loads(response.text.encode('utf8'))
    print(data['message'])
    return data['message']



