from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from seleniumwire import webdriver as webdriverwire
from selenium import webdriver

def initialize_webdriver_headless():
    chrome_options = webdriverwire.ChromeOptions()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--ignore-certificate-errors")  # Ignore SSL errors
    chrome_options.add_argument("--allow-insecure-localhost")  # Allow insecure SSL on localhost
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--no-sandbox")  # Required for Docker
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")

    seleniumwire_options = {
        'verify_ssl': False,
        'disable_encoding': True
    }

    driver = webdriverwire.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options,
        seleniumwire_options=seleniumwire_options
    )
    driver.maximize_window()
    return driver


def initialize_webdriver_visible():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")  # Required for Docker
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")


    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options,
    )
    driver.maximize_window()
    return driver