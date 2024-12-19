from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import NoSuchElementException, TimeoutException

def wait_for_element(driver, locator_type, locator_value, condition="presence",timeout=10):
    """
    Wait for an element based on the specified condition.

    :param driver: WebDriver instance
    :param locator_type: Locator type (e.g., By.XPATH, By.ID, etc.)
    :param locator_value: Locator value
    :param condition: Condition to wait for ("presence", "clickable", "visible")
    :param timeout: Maximum wait time in seconds
    :return: WebElement if found, else raises TimeoutException
    """
    try:
        if condition == "presence":
            return WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((locator_type, locator_value))
            )
        elif condition == "clickable":
            return WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((locator_type, locator_value))
            )
        elif condition == "visible":
            return WebDriverWait(driver, timeout).until(
                EC.visibility_of_element_located((locator_type, locator_value))
            )
        else:
            raise ValueError(f"Unsupported condition: {condition}")
    except TimeoutException as e:
        print(f"Timeout while waiting for element ({locator_type}, {locator_value}) with condition {condition}.")
        raise e


def get_element_value(driver, parent_class, input_xpath):
    """
    Locate a parent div and extract the value from an input field inside it.
    """
    try:
        parent_div = driver.find_element(By.CLASS_NAME, parent_class)
        input_field = parent_div.find_element(By.XPATH, input_xpath)
        value = input_field.get_attribute("value")
        return value
    except NoSuchElementException as e:
        print(f"Could not locate element inside parent class: {parent_class}")
        raise e


def scroll_into_view(driver, element):
    """
    Scroll an element into view.
    """
    driver.execute_script("arguments[0].scrollIntoView();", element)


def clear_and_type(input_element, text):
    """
    Clear an input field and type new text.
    """
    try:
        input_element.click()  # Ensure the field is focused
        input_element.clear()  # Clear the field
        input_element.send_keys(Keys.CONTROL + "a")  # Select all text (for JS-heavy fields)
        for _ in range(10):
            input_element.send_keys(Keys.BACKSPACE)  # Clear selected text
        for char in text:
            input_element.send_keys(char)  # Mimic typing
            time.sleep(0.01)  # Add a slight delay for natural typing effect
    except Exception as e:
        print(f"Error while entering text: {e}")
        raise

