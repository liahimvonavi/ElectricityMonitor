import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import csv
from datetime import datetime

load_dotenv()

class Relay_Manager:
    def __init__(self):
        self.url = os.getenv("CLOUD_URL")

        self.driver = None

    def log_inverter_operation(self, invertor, mode):
        with open("inverter_operation_log.csv", "a", newline="") as logfile:
            writer = csv.writer(logfile)
            writer.writerow([datetime.now().isoformat(), invertor, mode])

    def click(self, xpath):
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath))).click()

    def write(self, xpath, keys):
        input_elem = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        input_elem.send_keys(keys)
    def wait_for_loading_mask(self, timeout=20):
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "el-loading-mask")))
    def relay_mode(self, mode):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--window-size=1920,1080')
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get(self.url)
        self.write(xpath='//input[@placeholder="Input email or username"]', keys=os.getenv("CLOUD_ACC"))
        self.click(xpath='//span[@class="el-checkbox__inner"]')
        self.write(xpath='//input[@placeholder="Input password"]', keys=os.getenv("CLOUD_PASS") + Keys.ENTER)

        with open('invertors_links.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)

            main_window = self.driver.current_window_handle
            time.sleep(1)

            for row in reader:
                url = row['URL']
                inverter = row['INVERTOR']
                for attempt in range(3):
                    try:
                        self.driver.execute_script("window.open('');")
                        self.driver.switch_to.window(self.driver.window_handles[-1])

                        self.driver.get(url)
                        time.sleep(1)

                        self.click(xpath="//span[contains(@class, 'el-tree-node__label') and text()='Inverter Power Setting']")
                        if mode == "on":
                            self.write(xpath="//input[@type='text' and @placeholder='Input' and contains(@class, 'el-input__inner')]", keys="100")
                        else:
                            self.write(xpath="//input[@type='text' and @placeholder='Input' and contains(@class, 'el-input__inner')]", keys="5")

                        self.wait_for_loading_mask()
                        self.log_inverter_operation(inverter, mode)
                        self.click(xpath="//a[contains(@class, 'el-link') and contains(@class, 'el-link--primary')]/span[text()='Save']")
                        break

                    except Exception as e:
                        print(f"Failed to set inverter {inverter} to {mode}: {e}")
                        if attempt == 2:
                            self.log_inverter_operation(inverter, f"Failed after 3 tries {mode}: {e}")

                    finally:
                        self.driver.close()
                        self.driver.switch_to.window(main_window)

        self.driver.quit()
