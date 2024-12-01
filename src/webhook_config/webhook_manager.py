from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time

from src.db.repositories.app_repositories import set_webhook_details




def configure_webhook_product(driver, neuro_employees_href, verify_token: str, callback_url: str):
    """Update webhook callback URL and verify token."""
    webhooks_url = f"{neuro_employees_href}/webhooks/"
    driver.get(webhooks_url)
    print(f"Navigated to webhooks page: {webhooks_url}")
    edit_subscription_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="developer_app_body"]/div/div[2]/div/div/div[2]/div/table/tbody/tr/td[1]/a')
        )
    )
    edit_subscription_button.click()

    callback_url_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@name='callback_url']"))
    )
    callback_url_input.clear()
    callback_url_input.send_keys(callback_url)

    verify_token_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@name='verify_token']"))
    )
    verify_token_input.clear()
    verify_token_input.send_keys(verify_token)

    save_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and contains(text(), 'Verify and save')]"))
    )
    save_button.click()
    print("webhook updated successfully!")


def configure_webhook_for_instagram_api_product(driver, neuro_employees_href, verify_token: str, callback_url: str):
    api_setup_url = f"{neuro_employees_href}/instagram-business/API-Setup/"
    driver.get(api_setup_url)
    print(f"Navigated to API Setup page: {api_setup_url}")

    dropdown_config_webhook = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, f'//*[@id="developer_app_body"]/div/div/div/div[3]/div/div[1]/div/div/div/div[4]/div/div/div[1]/div/div/div[2]/div/div')
        )
    )
    dropdown_config_webhook.click()
    print("dropdown success!")

    try:
      edit_button = WebDriverWait(driver, 10).until(
          EC.element_to_be_clickable(
              (By.XPATH, f'//*[@id="js_2n"]/div[2]/div[1]/div[3]/div/div')
          )
      )
      if not edit_button:
          raise Exception("Кнопка с указанными текстовыми вариациями не найдена.")

      edit_button.click()
      print("Кнопка успешно нажата!")

      # Locate the input field for the callback URL
      callback_input = WebDriverWait(driver, 10).until(
          EC.presence_of_element_located((By.XPATH, "//input[@type='url']"))
      )
      driver.execute_script("arguments[0].scrollIntoView();", callback_input)
      callback_input.click()  # Ensure the field is focused
      callback_input.clear()  # Clear the field
      callback_input.send_keys(Keys.CONTROL + "a")  # Select all text (sometimes necessary for JS fields)
      callback_input.send_keys(Keys.BACKSPACE)  # Clear selected text
      callback_input.send_keys(callback_url)  # Enter new text
      print(f"Callback URL entered: {callback_url}")

      # Проверяем все элементы с одинаковым id и атрибутами
      # Проверяем наличие нужного input элемента
      # Locate the Verify Token input field
      parent_div = WebDriverWait(driver, 10).until(
          EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div[1]/div[1]/div/div/div/div/div[2]/div[1]/div[2]/div[2]/div/div[2]/div/div/div/div[1]/div[2]/div'))
      )
      print("Parent <div> located successfully.")
      # Locate the input field inside the parent <div>
      verify_token_input = parent_div.find_element(By.TAG_NAME, "input")
      print("Input field located inside the parent <div>.")

      # Scroll to the input field to make it visible
      driver.execute_script("arguments[0].scrollIntoView();", verify_token_input)

      # Focus and clear the input field
      verify_token_input.click()  # Ensure the input field is focused
      driver.execute_script("arguments[0].value = '';", verify_token_input)  # Clear any existing value
      print("Input field cleared.")

      # Enter the Verify Token value character by character
      for char in verify_token:
          verify_token_input.send_keys(char)  # Mimic typing
          time.sleep(0.1)  # Add a slight delay for natural typing effect
      print(f"Verify Token entered: {verify_token}")

      # Validate the entered value
      entered_value = verify_token_input.get_attribute("value")
      if entered_value == verify_token:
          print("Verify Token successfully entered and validated.")
      else:
          raise Exception(f"Failed to set Verify Token. Expected: '{verify_token}', Found: '{entered_value}'")

        # Locate the save button using the given XPath
      save_button = WebDriverWait(driver, 10).until(
          EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div[1]/div[1]/div/div/div/div/div[3]/div/div[2]/div'))
      )
      print("Save button located successfully.")

      # Scroll into view to ensure visibility
      driver.execute_script("arguments[0].scrollIntoView();", save_button)

      # Click the save button
      save_button.click()
      print("Save button clicked successfully.")

    except Exception as e:
          print(f"Ошибка при поиске или клике по элементу: {e}")

    input("Press Enter to close the browser...")
