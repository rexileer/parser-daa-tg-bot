from selenium import webdriver
import time

options = webdriver.ChromeOptions()
options.add_argument('start-maximized')
# options.add_argument('--headless') # Run Chrome in headless mode
# options.add_argument('--no-sandbox') # Bypass OS security model
# options.add_argument('--disable-dev-shm-usage') # overcome limited resource problems
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_experimental_option('excludeSwitches', ['enable-automation'])
options.add_experimental_option('useAutomationExtension', False)
driver = webdriver.Chrome(options=options)

url = "https://www.avito.ru/"

driver.get(url)
time.sleep(1)
driver.quit()