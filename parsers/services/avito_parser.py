import time
import random
import pickle
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from fake_useragent import UserAgent, FakeUserAgentError

class AvitoParser:
    def __init__(self, filters=None):
        self.filters = filters or {}
        self.driver = self._init_driver()
        self.logger = self._init_logger()
    
    def _init_driver(self):
        options = webdriver.ChromeOptions()
        try:
            ua = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0"
        except FakeUserAgentError:
            ua = UserAgent().chrome
        options.add_argument(f'user-agent={ua}')
        options.add_argument('start-maximized')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--incognito")
        options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(10)
        return driver
    
    def _init_logger(self):
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(__name__)
    
    def _human_delay(self, min_time=2, max_time=5):
        time.sleep(random.uniform(min_time, max_time))
    
    def _load_cookies(self):
        try:
            with open("cookies.pkl", "rb") as file:
                cookies = pickle.load(file)
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
            self.driver.refresh()
            self.logger.info("Cookies loaded")
        except FileNotFoundError:
            self.logger.warning("Cookies not found")
    
    def _set_filter(self, filter_name, value):
        wait = WebDriverWait(self.driver, 10)
        if filter_name == "price_from":
            price_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-marker='price-from/input']")))
        elif filter_name == "price_to":
            price_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-marker='price-to/input']")))
        else:
            return
        
        self.driver.execute_script("arguments[0].focus();", price_input)
        self._human_delay(1, 2)
        price_input.clear()
        self._human_delay(1, 2)
        for char in str(value):
            price_input.send_keys(char)
            self._human_delay(0.1, 0.2)
        self.driver.execute_script("arguments[0].dispatchEvent(new Event('blur'));", price_input)
        self._human_delay(1, 2)
        self.driver.execute_script("arguments[0].dispatchEvent(new Event('input'));", price_input)
    
    def _apply_filters(self):
        for filter_name, value in self.filters.items():
            self._set_filter(filter_name, value)
        self.logger.info("Filters applied")
        self._human_delay()
        
        submit_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-marker='search-filters/submit-button']"))
        )
        self.driver.execute_script("arguments[0].focus();", submit_button)
        submit_button.click()
        self.logger.info("Submit button clicked")
        self._human_delay()
    
    def _scroll_page(self):
        actions = ActionChains(self.driver)
        for _ in range(random.randint(3, 7)):
            offset_x = random.randint(50, 200)
            offset_y = random.randint(50, 200)
            actions.move_by_offset(offset_x, offset_y).perform()
            self.driver.execute_script("window.scrollBy(0, arguments[0]);", random.randint(100, 300))
            self.logger.info("Scrolling")
            self._human_delay()
    
    def _parse_ads(self):
        ads = self.driver.find_elements(By.CSS_SELECTOR, "div[data-marker='item']")
        if not ads:
            self.logger.warning("No ads found on the page")
        
        for ad in ads:
            try:
                title = ad.find_element(By.CSS_SELECTOR, "h3").text
                price = ad.find_element(By.CSS_SELECTOR, "p[data-marker='item-price'] span").text
                link = ad.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                self.logger.info(f"Title: {title}, Price: {price}, Link: {link}")
            except Exception as ex:
                self.logger.error(f"Error processing ad: {ex}")
    
    def _save_cookies(self):
        with open("cookies.pkl", "wb") as file:
            pickle.dump(self.driver.get_cookies(), file)
        self.logger.info("Cookies saved")
    
    def parse(self):
        try:
            url = "https://www.avito.ru/all/avtomobili?s=104"
            self.logger.info("Opening avito.ru")
            self.driver.get(url)
            self.driver.set_page_load_timeout(30)
            self.logger.info("Opened avito.ru")
            self._human_delay()
            
            self._load_cookies()
            self._apply_filters()
            self._scroll_page()
            self._parse_ads()
            self._save_cookies()
            
        except Exception as ex:
            self.logger.error(f"Unhandled error: {ex}")
        finally:
            self.driver.quit()
            self.logger.info("Driver closed")

if __name__ == '__main__':
    parser = AvitoParser(filters={"price_from": 1000000, "price_to": 1200000})
    parser.parse()
