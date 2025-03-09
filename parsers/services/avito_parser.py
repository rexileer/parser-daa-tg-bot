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

def human_delay(min_time=2, max_time=5):
    """Добавляет случайную задержку между действиями для имитации человеческого поведения."""
    time.sleep(random.uniform(min_time, max_time))

def parse_avito(filters=None):
    """Основная функция для парсинга объявлений на Avito."""
    # Инициализация опций драйвера
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
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)

    # Инициализация драйвера
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    
    # Инициализация логгера
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    try:
        # Открытие Avito с новыми автомобилями
        url = "https://www.avito.ru/all/avtomobili?s=104"
        logger.info("Opening avito.ru")
        driver.get(url)
        driver.set_page_load_timeout(30)
        logger.info("Opened avito.ru")
        human_delay()

        # Загрузка cookies, если они есть
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
        
        # Взаимодействие с фильтрами
        try:
            # Ввод min цены с учетом случайных задержек
            price_from_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-marker='price-from/input']")))
            
            driver.execute_script("arguments[0].focus();", price_from_input)
            human_delay(1, 2)
            price_from_input.clear()
            human_delay(1, 2)
            for char in "1000000":
                price_from_input.send_keys(char)
                human_delay(0.1, 0.2)
            driver.execute_script("arguments[0].dispatchEvent(new Event('blur'));", price_from_input)
            human_delay(1, 2)
            driver.execute_script("arguments[0].dispatchEvent(new Event('input'));", price_from_input)
            
            
            # Ввод max цены с учетом случайных задержек
            price_to_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-marker='price-to/input']")))
            
            driver.execute_script("arguments[0].focus();", price_to_input)
            human_delay(1, 2)
            price_to_input.clear()
            human_delay(1, 2)
            for char in "1200000":
                price_to_input.send_keys(char)
                human_delay(0.1, 0.2)
            driver.execute_script("arguments[0].dispatchEvent(new Event('blur'));", price_to_input)
            human_delay(1, 2)
            driver.execute_script("arguments[0].dispatchEvent(new Event('input'));", price_to_input)
            
            logger.info("Input price")
            human_delay()


            # Нажатие на кнопку "Применить"
            submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-marker='search-filters/submit-button']")))
            human_delay(1, 2)
            driver.execute_script("arguments[0].focus();", submit_button)
            submit_button.click()
            logger.info("Submit button clicked")
            human_delay()
        except Exception as e:
            logger.error(f"Error interacting with filters: {e}")

        # Скроллинг страницы с случайным смещением
        actions = ActionChains(driver)
        for _ in range(random.randint(3, 7)):
            offset_x = random.randint(50, 200)
            offset_y = random.randint(50, 200)
            actions.move_by_offset(offset_x, offset_y).perform()
            driver.execute_script("window.scrollBy(0, arguments[0]);", random.randint(100, 300))
            logger.info("Scrolling")
            human_delay()

        # Извлечение информации о объявлениях
        ads = driver.find_elements(By.CSS_SELECTOR, "div[data-marker='item']")
        if not ads:
            logger.warning("No ads found on the page")

        for ad in ads:
            try:
                title = ad.find_element(By.CSS_SELECTOR, "h3").text
                price = ad.find_element(By.CSS_SELECTOR, "p[data-marker='item-price'] span").text
                link = ad.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                logger.info(f"Title: {title}, Price: {price}, Link: {link}")
            except Exception as ex:
                logger.error(f"Error processing ad: {ex}")

        # Сохранение cookies
        with open("cookies.pkl", "wb") as file:
            pickle.dump(driver.get_cookies(), file)
        logger.info("Cookies saved")

    except Exception as ex:
        # Обработка ошибок
        logger.error(f"Unhandled error: {ex}")
    finally:
        # Закрытие драйвера
        driver.quit()
        logger.info("Driver closed")

if __name__ == '__main__':
    parse_avito()
