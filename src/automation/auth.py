from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def perform_login(driver, email, password):
    # Wait for email input and enter the email
    email_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'email')))
    email_input.send_keys(email)

    # Enter the password
    password_input = driver.find_element(By.ID, 'pass')
    password_input.send_keys(password)

    # Click the login button
    login_button = driver.find_element(By.XPATH, '//*[@id="loginbutton"]')
    print("located")
    login_button.click()

    # Wait and refresh to ensure login is complete
    driver.refresh()
    print("Login successful.")
