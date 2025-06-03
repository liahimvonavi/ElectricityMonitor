import os

from selenium import webdriver
from bs4 import BeautifulSoup
import time
import csv
from dotenv import load_dotenv

load_dotenv()

threshold = 20
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--window-size=1920,1080')
driver = webdriver.Chrome(options=chrome_options)
driver.get(os.getenv('PRICES_URL'))

time.sleep(5)

soup = BeautifulSoup(driver.page_source, 'html.parser')
tables = soup.find_all('table')
target_table = tables[2]

rows = []
for row in target_table.find_all('tr'):
    cols = [td.text.strip() for td in row.find_all(['td', 'th'])]
    rows.append(cols)

driver.quit()


header = rows[0]
last_col_idx = len(header) - 1
last_day = header[last_col_idx]

print(f"Данни за {last_day}")
print("Час\tЦена (BGN/MWh)")

hour_prices = {}
for i in range(1, len(rows), 2):
    hour_range = rows[i][0]
    start_hour_cet = int(hour_range.split(' - ')[0])
    if 6 <= start_hour_cet <= 18:
        price = round(float(rows[i][last_col_idx]) * 1.95583, 2)
        start_hour_bg = (start_hour_cet + 1)
        hour_prices[start_hour_bg] = price

with open("relay_plan.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(['hour', 'state'])
    for hour in sorted(hour_prices):
        if hour_prices[hour] < threshold:
            state = "off"
        else:
            state = "on"
        writer.writerow([hour, state])
        print(f"{hour}:00 - {hour + 1}:00 -> {hour_prices[hour]} BGN -> {state.upper()}")
    writer.writerow(['20', 'on'])
