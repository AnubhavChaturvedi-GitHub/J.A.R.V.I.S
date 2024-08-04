import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import logging
from os import getcwd

logging.getLogger('selenium').setLevel(logging.WARNING)


chrome_options = Options()
chrome_options.add_argument("--headless")

chrome_options.add_argument("--disable-blink-features=AutomationControlled")

chrome_driver_path = f"{getcwd()}\\chromedriver.exe"
service = Service(executable_path=chrome_driver_path)

# Setting up the Chrome driver with the service and options
driver = webdriver.Chrome(service=service, options=chrome_options)


def get_internet_speed():
    try:
        driver.get("https://fast.com/")
        time.sleep(11)
        WebDriverWait(driver,60).until(EC.presence_of_all_elements_located((By.ID,'speed-value')))
        speed_value = driver.find_element(By.ID,'speed-value')
        speed_value = speed_value.text
        return speed_value
    except Exception as e:
        print(e)
    
