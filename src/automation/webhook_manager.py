import time
from sqlalchemy.orm import Session
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
from src.automation.utils import (
    wait_for_element,
    scroll_into_view,
    clear_and_type,
    get_element_value
)



def configure_webhook_product(driver, verify_token: str, webhook_callback_url: str):
    """Update webhook callback URL and verify token."""

    try:
        edit_subscription_button_xpath = '//*[@id="developer_app_body"]/div/div[2]/div/div/div[2]/div/table/tbody/tr/td[1]/a'
        edit_subscription_button = wait_for_element(driver, By.XPATH,edit_subscription_button_xpath,condition="clickable")
        edit_subscription_button.click()
        print("Webhook Edit button clicked!")
        callback_url_input_xpath = "//input[@name='callback_url']"
        callback_url_input = wait_for_element(driver, By.XPATH, callback_url_input_xpath, condition="presence")
        clear_and_type(callback_url_input, webhook_callback_url)

        verify_token_input_xpath = "//input[@name='verify_token']"
        verify_token_input =  wait_for_element(driver, By.XPATH, verify_token_input_xpath, condition="presence")
        clear_and_type(verify_token_input, verify_token)
        print("input fields entered!")

        save_button_xpath = "//button[@type='submit' and contains(text(), 'Verify and save')]"
        save_button = wait_for_element(driver, By.XPATH, save_button_xpath, condition="clickable")
        save_button.click()
        print(f"Webhook Service Updated!")
    except Exception as e:
        print(f"An error occurred: {e}")
        raise WebDriverException


def configure_instagram_api_product(driver, verify_token: str, webhook_callback_url: str, handle_code_url: str, session: Session):
    try:
        # Step 1.1: Retrieve the Instagram App ID
        app_id_xpath = '/html/body/div[1]/div[5]/div[1]/div/div[5]/div[1]/div[2]/div[2]/div/div/div/div/div/div[3]/div/div[1]/div/div/div/div[2]/div/div/div/div/div[1]/div[2]/div/div[2]/a/span/div'
        app_id_element = wait_for_element(driver, By.XPATH, app_id_xpath, condition="presence")
        inst_app_id = app_id_element.text
        print(f"Retrieved Instagram App ID: {inst_app_id}")

        # Step 1.2: Click the "Show" button
        show_button_xpath = "//div[contains(@class, 'x8t9es0') and text()='Show']"
        show_button = wait_for_element(driver, By.XPATH, show_button_xpath, condition="clickable")
        show_button.click()

        # Step 1.3: Retrieve the updated value
        parent_class = "xhk9q7s.x1otrzb0.xo71vjh.x5pf9jr.x78zum5.xdt5ytf.x1iyjqo2"
        input_xpath = ".//input[@type='text']"
        time.sleep(4)
        inst_app_secret = get_element_value(driver, parent_class, input_xpath)
        print(f"Instagram app secret: {inst_app_secret}")

        # Step 2: Dropdown Configure Webhook open
        dropdown_xpath = '//*[@id="developer_app_body"]/div/div/div/div[3]/div/div[1]/div/div/div/div[4]/div/div/div[1]/div/div/div[2]/div/div'
        dropdown_configure_webhook = wait_for_element(driver, By.XPATH, dropdown_xpath, condition="clickable")
        dropdown_configure_webhook.click()
        print("Dropdown Configure Webhook clicked ! (open)")

        # Step 2.1: Click "Edit" button
        edit_button_full_xpath = '/html/body/div[1]/div[5]/div[1]/div/div[5]/div[1]/div[2]/div[2]/div/div/div/div/div/div[3]/div/div[1]/div/div/div/div[4]/div/div/div[2]/div[2]/div[1]/div[3]/div/div'
        edit_button = wait_for_element(driver, By.XPATH, edit_button_full_xpath, condition="clickable")
        edit_button.click()
        print("Edit button clicked!")

        # Step 2.2: Set Callback URL
        callback_input_xpath = "//input[@type='url']"
        callback_input = wait_for_element(driver, By.XPATH, callback_input_xpath, condition="presence")
        scroll_into_view(driver, callback_input)
        clear_and_type(callback_input, webhook_callback_url)
        print(f"Callback URL entered: {webhook_callback_url}")

        # Step 2.3: Set Verify Token
        parent_div_full_xpath = '/html/body/div[4]/div[1]/div[1]/div/div/div/div/div[2]/div[1]/div[2]/div[2]/div/div[2]/div/div/div/div[1]/div[2]/div'
        parent_div = wait_for_element(driver, By.XPATH, parent_div_full_xpath, condition="presence")
        verify_token_input = parent_div.find_element(By.TAG_NAME, "input")
        scroll_into_view(driver, verify_token_input)
        clear_and_type(verify_token_input, verify_token)
        print(f"Input field text entered: {verify_token}")

        # Step 2.4: Save Changes
        save_button_xpath = '/html/body/div[4]/div[1]/div[1]/div/div/div/div/div[3]/div/div[2]/div'
        save_button = wait_for_element(driver, By.XPATH, save_button_xpath, condition="presence")
        scroll_into_view(driver, save_button)
        save_button.click()
        print("Save button clicked successfully.")


        # Step 3: Dropdown Business Login open:
        dropdown_business_login_xpath = '/html/body/div[1]/div[5]/div[1]/div/div[5]/div[1]/div[2]/div[2]/div/div/div/div/div/div[3]/div/div[1]/div/div/div/div[5]/div/div/div[1]/div/div/div[2]/div/div'
        dropdown_business_login = wait_for_element(driver, By.XPATH, dropdown_business_login_xpath, condition="clickable")
        scroll_into_view(driver, dropdown_business_login)
        dropdown_business_login.click()
        print("Dropdown Business Login settings clicked!")

        # Step 3.1: Business Login Settings
        business_login_settings_button_xpath = '/html/body/div[1]/div[5]/div[1]/div/div[5]/div[1]/div[2]/div[2]/div/div/div/div/div/div[3]/div/div[1]/div/div/div/div[5]/div/div/div[2]/div/div/div[2]/div'
        business_login_settings_button = wait_for_element(driver, By.XPATH, business_login_settings_button_xpath, condition="clickable")
        business_login_settings_button.click()
        print("Business login button clicked!")
        time.sleep(2)

        # Step 3.2: Set handle code url
        oauth_redirect_uris_input_xpath = "//input[@aria-autocomplete='list' and @role='combobox']"
        oauth_redirect_uris_input = wait_for_element(driver, By.XPATH, oauth_redirect_uris_input_xpath, condition="presence")
        scroll_into_view(driver, oauth_redirect_uris_input)
        oauth_redirect_uris_input.click()
        print("OAuth redirect uris input clicked!")
        driver.execute_script("arguments[0].value = '';", oauth_redirect_uris_input)
        clear_and_type(oauth_redirect_uris_input, handle_code_url)
        oauth_redirect_uris_input.send_keys(Keys.ENTER)

        # Step 3.3 Save button
        save_button_parent_class_name = "x6s0dn4.x78zum5.x1q0g3np.xozqiw3.x2lwn1j.xeuugli.x19lwn94.x1swvt13.x1pi30zi.x1l90r2v.x1y1aw1k.x1c4vz4f.x2lah0s"
        parent_div = wait_for_element(driver, By.CLASS_NAME, save_button_parent_class_name, condition="presence")
        save_button = parent_div.find_element(By.XPATH,".//div[@role='button' and @aria-busy='false' and @tabindex='0']//div[text()='Opslaan']")
        save_button.click()
        time.sleep(4)

        # Step 3.4 Get Embed URL
        copy_input_field_xpath = "html/body/div[1]/div[5]/div[1]/div/div[5]/div[1]/div[2]/div[2]/div/div/div/div/div/div[3]/div/div[1]/div/div/div/div[5]/div/div/div[2]/div/div/div[1]/div[1]/div/div[2]/div[1]/div[2]/div/div/input"
        copy_value = wait_for_element(driver, By.XPATH, copy_input_field_xpath, condition="presence")
        embed_url = copy_value.get_attribute("value")
        print("Embed URL entered: " + embed_url)
        print(f"Instagram API Updated:")
        return inst_app_id, inst_app_secret, embed_url
    except Exception as e:
        print(f"An error occurred in main workflow: {e}")

