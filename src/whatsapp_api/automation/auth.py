from selenium.webdriver.common.by import By
from src.utils.automation_tools import wait_for_element
import time

def perform_login(driver, email, password):
    # Enter the email with a slight delay for each character
    email_input = wait_for_element(driver, By.XPATH, '//*[@id="login"]', condition="presence")
    for char in email:
        email_input.send_keys(char)
        time.sleep(0.03)  # Human-like delay per character

    time.sleep(0.5)  # Pause before entering password

    # Enter the password with a slight delay for each character
    password_input = driver.find_element(By.XPATH, '//*[@id="password"]')
    for char in password:
        password_input.send_keys(char)
        time.sleep(0.1)  # Human-like delay per character

    time.sleep(0.5)  # Pause before clicking login button

    # Click the login button
    login_button = driver.find_element(By.XPATH, '//*[@id="root"]/main/div/div[2]/div/form/div[4]/button')
    login_button.click()

    time.sleep(.5)  # Wait to ensure login is processing
    driver.refresh()  # Refresh to confirm login
    time.sleep(.5)
    print("Login successful.")