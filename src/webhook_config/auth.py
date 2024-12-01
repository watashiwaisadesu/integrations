# auth.py

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def perform_login(driver, email, password):
    driver.get('https://www.facebook.com/login/')

    email_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'email')))
    email_input.send_keys(email)

    password_input = driver.find_element(By.ID, 'pass')
    password_input.send_keys(password)

    login_button = driver.find_element(By.XPATH, '//*[@id="loginbutton"]')
    login_button.click()

    print("Login successful.")
