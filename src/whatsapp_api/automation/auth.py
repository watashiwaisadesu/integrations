import logging
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from src.utils.automation_tools import wait_for_element
# Import your custom exceptions
from src.utils.errors_handler import InternalServerError

logger = logging.getLogger(__name__)

def perform_login(driver, email: str, password: str):
    """
    Logs into the application using the provided email and password.
    Includes human-like typing delays and logs important steps/errors.
    """
    logger.info("Starting perform_login process.")

    try:
        # Enter the email with a slight delay for each character
        logger.debug("Waiting for email input field.")
        email_input = wait_for_element(driver, By.XPATH, '//*[@id="login"]', condition="presence")
        logger.debug("Email input field found. Typing email...")
        for char in email:
            email_input.send_keys(char)
            time.sleep(0.03)  # Human-like delay per character

        time.sleep(0.5)  # Pause before entering password

        # Enter the password
        logger.debug("Locating password input field.")
        password_input = driver.find_element(By.XPATH, '//*[@id="password"]')
        logger.debug("Password input field found. Typing password...")
        for char in password:
            password_input.send_keys(char)
            time.sleep(0.1)

        time.sleep(0.5)  # Pause before clicking login button

        logger.debug("Locating login button.")
        login_button = driver.find_element(By.XPATH, '//*[@id="root"]/main/div/div[2]/div/form/div[4]/button')
        logger.debug("Clicking login button.")
        login_button.click()

        # Short wait to ensure login is processing
        time.sleep(0.5)

        logger.debug("Refreshing page to confirm login.")
        driver.refresh()
        time.sleep(0.5)

        logger.info("Login successful.")

    except NoSuchElementException as e:
        logger.error(f"Element not found during login: {e}")
        # Raise a custom 500-level error (or a more specific one if you prefer).
        raise InternalServerError("Element not found during login.") from e

    except Exception as e:
        logger.error(f"Unexpected error in perform_login: {e}")
        # Raise a generic internal server error for any other issue.
        raise InternalServerError("Unexpected error in perform_login.") from e
