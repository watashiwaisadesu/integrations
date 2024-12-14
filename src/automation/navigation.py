from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time




def navigate_to_login_page(driver):
    driver.get('https://www.facebook.com/login/')
    print(f"Navigated to login page (FACEBOOK)")
    time.sleep(2)


def navigate_to_my_apps(driver):
    """Navigate to the 'My Apps' section."""
    driver.get('https://developers.facebook.com/apps/')
    print(f"Navigated to my apps")
    time.sleep(2)


def navigate_to_webhook_service(driver, app_href):
    webhooks_url = f"{app_href}/webhooks/"
    driver.get(webhooks_url)
    print(f"Navigated to webhooks page: {webhooks_url}")

def navigate_to_instagramapi_service(driver, app_href):
    api_setup_url = f"{app_href}/instagram-business/API-Setup/"
    driver.get(api_setup_url)
    print(f"Navigated to API Setup page: {api_setup_url}")

def locate_app_href(driver, app_name: str):
    """Locate the app by name and return its href link."""
    try:
        # Wait for the app link to be located
        app_link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//div[contains(text(), '{app_name}')]/ancestor::a"))
        )
        app_href = app_link.get_attribute("href")
        print(f"{app_name} app located: {app_href}")
        return app_href
    except Exception:
        # Raise a custom error if the app is not found
        raise ValueError(f"The app '{app_name}' does not exist or could not be located.")
