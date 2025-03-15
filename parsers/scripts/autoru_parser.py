import json
import time
import random
import re
import logging
import redis
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from config import REDIS_HOST, REDIS_PORT

class AutoruParser:
    def __init__(self, filters=None, redis_host=REDIS_HOST, redis_port=REDIS_PORT, redis_db=0):
        self.filters = filters or {}
        self.redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)
        self.driver = self._init_driver()
        self.logger = self._init_logger()
    
    def _init_driver(self):
        options = webdriver.ChromeOptions()
        # Используем фиксированный desktop user agent
        desktop_ua = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        options.add_argument(f'user-agent={desktop_ua}')
        options.add_argument('--headless')
        options.add_argument('start-maximized')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--incognito')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--disable-images")
        options.add_argument("--disable-extensions")
        options.add_argument("--blink-settings=imagesEnabled=false")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-client-side-phishing-detection")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        driver = webdriver.Remote(
            command_executor="http://chrome_driver:4444/wd/hub",
            options=options,
        )
        driver.implicitly_wait(1)
        return driver
    
    def _init_logger(self):
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(__name__)
    
    def _extract_autoru_id(self, url: str) -> str | None:
        match = re.search(r'/(\d+)-\w+/', url)
        if not match:
            match = re.search(r'(\d+)$', url)
        return match.group(1) if match else None
    
    def _human_delay(self, min_time=2, max_time=5):
        time.sleep(random.uniform(min_time, max_time))
        
    def _human_mouse(self, min_time=2, max_time=5):
        actions = ActionChains(self.driver)
        try:
            submit_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li[data-id='history']"))
            )
        except Exception as e:
            self.logger.warning(f"Элемент для движения мыши не найден: {e}")
            return
        for _ in range(random.randint(min_time, max_time)):
            offset_x = random.randint(10, 50)
            offset_y = random.randint(10, 50)
            actions.move_to_element_with_offset(submit_button, offset_x, offset_y).perform()
            self.driver.execute_script("window.scrollBy(0, arguments[0]);", random.randint(100, 300))
            self.logger.info("Scrolling")
            self._human_delay(0.2, 0.7)
    
    def _parse_ads(self):
        ads = self.driver.find_elements(By.CSS_SELECTOR, "div[data-seo='listing-item']")
        new_ads = []
        for ad in ads[:10]:
            try:
                link = ad.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                ad_id = self._extract_autoru_id(link)
                self.logger.info(f"Processing ad {ad_id}")
                if not self.redis_client.exists(f"{ad_id}"):
                    new_ads.append({'link': link})
            except Exception as ex:
                self.logger.error(f"Error processing ad: {ex}")
                continue
        self.logger.info(f"Found {len(new_ads)} new ads")
        self._human_mouse(2, 5)
        return new_ads
    
    def _parse_characteristics(self):
        characteristics = {}
        exclude_values = {"Неизвестно", "Нет данных"}
        try:
            li_elements = self.driver.find_elements(By.CSS_SELECTOR, "li[class^='CardInfoRow']")
            for li in li_elements:
                try:
                    item = li.find_elements(By.TAG_NAME, "div")
                    if item and len(item) >= 2:
                        key = item[0].text
                        value = item[1].text
                        if key and value and value not in exclude_values:
                            characteristics[key] = value
                        else:
                            self.logger.warning(f"Проблема с разбором: {li.get_attribute('outerHTML')}")
                except Exception as e:
                    self.logger.error(f"Ошибка при обработке {li.get_attribute('outerHTML')}: {e}")
        except Exception as e:
            self.logger.error(f"Ошибка при парсинге характеристик: {e}")
        return characteristics
    
    def _parse_characteristics_new(self):
        characteristics = {}
        exclude_values = {"Неизвестно", "Нет данных"}
        try:
            li_elements = self.driver.find_elements(By.CSS_SELECTOR, "li[class^='CardInfoGroupedRow']")
            for li in li_elements:
                try:
                    key_element = li.find_element(By.CSS_SELECTOR, "div[class^='CardInfoGroupedRow__cellTitle']")
                    key = key_element.text.strip() if key_element else None
                    value_elements = li.find_elements(By.CSS_SELECTOR, "div[class^='CardInfoGroupedRow__cellValue'], span, a")
                    values = [el.text.strip() for el in value_elements if el.text.strip()]
                    value = " / ".join(values) if values else None
                    if key and value and value not in exclude_values:
                        characteristics[key] = value
                    else:
                        self.logger.warning(f"Проблема с разбором: {li.get_attribute('outerHTML')}")
                except Exception as e:
                    self.logger.error(f"Ошибка при обработке {li.get_attribute('outerHTML')}: {e}")
        except Exception as e:
            self.logger.error(f"Ошибка при парсинге характеристик: {e}")
        return characteristics
    
    def _extract_info(self, url: str) -> list[str] | None:
        pattern = r'https://auto.ru/cars/(new/group|used/sale)/([^/]+)/([^/]+)/'
        match = re.match(pattern, url)
        if match:
            return list(match.groups())
        return None
    
    def _normalize_car_data(self, raw_data: dict) -> dict:
        def __normalize_int(value, default=0):
            try:
                return int(re.sub(r'\D', '', str(value)))
            except ValueError:
                return default
        
        def __normalize_str(value):
            return str(value).strip().lower() if value else "unknown"
        
        seller_mapping = {"dealer": "автодилер", "private": "частное лицо"}
        ad_type_mapping = {"new": "новый", "used": "второй рынок"}
        
        return {
            "platform": __normalize_str(raw_data.get("platform")),
            "link": raw_data.get("link", ""),
            "name": __normalize_str(raw_data.get("name")),
            "year": __normalize_int(raw_data.get("year"), default="unknown"),
            "image": raw_data.get("image", ""),
            "price": __normalize_int(raw_data.get("price"), default="unknown"),
            "city": __normalize_str(raw_data.get("city")),
            "brand": __normalize_str(raw_data.get("brand")),
            "model": __normalize_str(raw_data.get("model")),
            "mileage": __normalize_int(raw_data.get("mileage"), default="unknown"),
            "engine": __normalize_str(raw_data.get("engine")),
            "color": __normalize_str(raw_data.get("color")),
            "gearbox": __normalize_str(raw_data.get("gearbox")),
            "drive": __normalize_str(raw_data.get("drive")),
            "steering": __normalize_str(raw_data.get("steering")),
            "owners": __normalize_int(raw_data.get("owners"), default="unknown"),
            "body_type": __normalize_str(raw_data.get("body_type")),
            "condition": __normalize_str(raw_data.get("condition")),
            "ad_type": ad_type_mapping.get(__normalize_str(raw_data.get("ad_type")), "unknown"),
            "seller": seller_mapping.get(__normalize_str(raw_data.get("seller")), "unknown")
        }
    
    def _parse_details(self, ad):
        self.driver.get(ad['link'])
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "img")))
        except Exception as e:
            self.logger.error(f"Ошибка ожидания загрузки изображений: {e}")
            return None
        self._human_mouse(1, 2)
        self._human_delay(1, 3)
        
        try:
            extracted_info = self._extract_info(ad['link'])
            if not extracted_info:
                self.logger.error(f"Не удалось извлечь информацию из URL: {ad['link']}")
                return None
            # Если тип объявления "new/group", используем новые характеристики
            characteristics = self._parse_characteristics_new() if extracted_info[0] == "new/group" else self._parse_characteristics()
            try:
                title = self.driver.find_element(By.CSS_SELECTOR, "h1").text
            except Exception as e:
                self.logger.error(f"Не удалось получить заголовок: {e}")
                title = ""
            title_parts = title.rsplit(", ", 1)
            details = {
                "platform": "autoru",
                "link": ad['link'],
                "name": title_parts[0] if len(title_parts) > 1 else title,
                "year": title_parts[1] if len(title_parts) > 1 else None,
                "image": self.driver.find_element(By.CSS_SELECTOR, "img[class='ImageGalleryDesktop__image']").get_attribute("src"),
                "price": self.driver.find_element(By.CSS_SELECTOR, "span[class='OfferPriceCaption__price']").text,
                "city": self.driver.find_element(By.CSS_SELECTOR, "div[class^='CardSellerNamePlace2__address'] span[class^='MetroListPlace__regionName']").text,
                "brand": extracted_info[1] if extracted_info else None,
                "model": extracted_info[2] if extracted_info else None,
                "mileage": characteristics.get('Пробег'),
                "engine": characteristics.get('Двигатель'),
                "color": characteristics.get('Цвет'),
                "gearbox": characteristics.get('Коробка'),
                "drive": characteristics.get('Привод'),
                "steering": characteristics.get('Руль'),
                "owners": characteristics.get('Владельцы'),
                "body_type": characteristics.get('Кузов'),
                "condition": characteristics.get('Состояние'),
                "ad_type": "new" if extracted_info and extracted_info[0] == "new/group" else "used",
                "seller": "group" if extracted_info and extracted_info[0] == "new/group" else "private",
            }
            ad_id = self._extract_autoru_id(ad['link'])
            normalized_details = self._normalize_car_data(details)
            self.redis_client.setex(f"{ad_id}", 1800, json.dumps(normalized_details, ensure_ascii=False))
            self.logger.info(f"Saved ad {ad_id} to Redis")
            return normalized_details
        except Exception as ex:
            self.logger.error(f"Error parsing ad details: {ex}")
        return None
    
    def _cookies_accept(self):
        try:
            accept_cookies = self.driver.find_element(By.CSS_SELECTOR, "a[id='confirm-button']")
            accept_cookies.click()
            self.logger.info("Cookies accepted")
        except Exception as e:
            self.logger.info("Не удалось принять cookies, возможно их нет на странице.")
    
    def parse(self):
        while True:
            try:
                self.driver.delete_all_cookies()
                url = "https://auto.ru/rossiya/cars/all/?sort=cr_date-desc"
                self.logger.info("Opening auto.ru")
                self.driver.get(url)
                self.driver.implicitly_wait(10)
                self.logger.info("Opened auto.ru")
                self._cookies_accept()
                self._human_delay()
                self._human_mouse(1, 2)
                try:
                    WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div[class='ListingItem']"))
                    )
                    self.logger.info("Объявления загружены, начинаем парсинг")
                except Exception as e:
                    self.logger.error(f"Ошибка ожидания объявлений: {e}")
                    self._human_delay(5, 10)
                    continue
                new_ads = self._parse_ads()
                if new_ads:
                    count = 0
                    for ad in new_ads:
                        try:
                            count += 1
                            self.logger.info(f"Processing ad {count}/{len(new_ads)}")
                            details = self._parse_details(ad)
                            if details:
                                self.logger.info(f"New ad: {details}")
                        except Exception as ex:
                            self.logger.error(f"Error processing ad: {ex}")
                            continue
                else:
                    self.logger.info("No new ads found.")
                    self._human_delay(5, 10)
                self._human_delay(5, 10)
            except Exception as ex:
                self.logger.error(f"Unhandled error: {ex} \n Возможна блокировка IP или другая ошибка. Перезапуск через 5 минут.")
                self.driver.quit()
                self._human_delay(300, 350)
                self.driver = self._init_driver()
            finally:
                self.logger.info("Iteration complete.")

if __name__ == '__main__':
    parser = AutoruParser()
    parser.parse()
