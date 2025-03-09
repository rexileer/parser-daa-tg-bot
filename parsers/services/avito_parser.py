import time
import random
import pickle
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from fake_useragent import UserAgent

def human_delay(min_time=2, max_time=5):
    time.sleep(random.uniform(min_time, max_time))

def parse_avito(filters=None):
    options = webdriver.ChromeOptions()
    ua = UserAgent()
    options.add_argument(f'user-agent={ua.random}')  # Установка случайного User-Agent
    options.add_argument('start-maximized')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(options=options)

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    try:
        url = "https://www.avito.ru/all/avtomobili?s=104"
        driver.get(url)
        logger.info("Opened avito.ru")
        human_delay()

        try:
            with open("cookies.pkl", "rb") as file:
                cookies = pickle.load(file)
                for cookie in cookies:
                    driver.add_cookie(cookie)
            driver.refresh()
            logger.info("Cookies loaded")
        except FileNotFoundError:
            logger.warning("Cookies not found")

        wait = WebDriverWait(driver, 10)
        try:
            price_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-marker='price/to']")))
            price_input.send_keys("100000")
            logger.info("Input price")
            human_delay()

            submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-marker='search-filters/submit-button']")))
            submit_button.click()
            logger.info("Submit button clicked")
            human_delay()
        except Exception as e:
            logger.error(f"Error interacting with filters: {e}")

        actions = ActionChains(driver)
        for _ in range(random.randint(3, 7)):
            actions.move_by_offset(random.randint(50, 300), random.randint(50, 300)).perform()
            driver.execute_script("window.scrollBy(0, arguments[0]);", random.randint(100, 500))
            logger.info("Scrolling")
            human_delay()

        ads = driver.find_elements(By.CSS_SELECTOR, "div[data-marker='item']")
        if not ads:
            logger.warning("No ads found on the page")

        for ad in ads:
            try:
                title = ad.find_element(By.CSS_SELECTOR, "h3").text
                price = ad.find_element(By.CSS_SELECTOR, "span[data-marker='item-price']").text
                link = ad.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                logger.info(f"Title: {title}, Price: {price}, Link: {link}")
            except Exception as ex:
                logger.error(f"Error processing ad: {ex}")

        with open("cookies.pkl", "wb") as file:
            pickle.dump(driver.get_cookies(), file)
        logger.info("Cookies saved")

    except Exception as ex:
        logger.error(f"Unhandled error: {ex}")
    finally:
        driver.quit()
        logger.info("Driver closed")

if __name__ == '__main__':
    parse_avito()
