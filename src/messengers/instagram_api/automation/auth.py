from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def perform_login(driver, email, password):
    # Wait for email input and enter the email
    email_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'email')))
    for char in email:
        email_input.send_keys(char)
        time.sleep(0.03)  # Human-like delay per character

    # Enter the password
    password_input = driver.find_element(By.ID, 'pass')
    for char in password:  # Use 'password' instead of 'email'
        password_input.send_keys(char)
        time.sleep(0.03)  # Human-like delay per character

    # Click the login button
    login_button = driver.find_element(By.XPATH, '//*[@id="loginbutton"]')
    print("Login button located.")
    login_button.click()

    # Wait and refresh to ensure login is complete
    driver.refresh()
    print("Login successful.")
