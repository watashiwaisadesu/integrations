# navigation.py

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def navigate_to_my_apps(driver):
    """Navigate to the 'My Apps' section."""
    driver.get('https://developers.facebook.com/apps/')

def locate_neuro_employees(driver, app_name: str):
    """Locate the 'neuro-employees' app."""
    neuro_employees_link = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, f"//div[contains(text(), '{app_name}')]/ancestor::a"))
    )
    neuro_employees_href = neuro_employees_link.get_attribute("href")
    print(f"'neuro-employees' app located: {neuro_employees_href}")
    return neuro_employees_href
