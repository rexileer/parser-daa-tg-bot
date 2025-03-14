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
from fake_useragent import UserAgent, FakeUserAgentError
from config import REDIS_HOST, REDIS_PORT

class AvitoParser:
    def __init__(self, redis_host=REDIS_HOST, redis_port=REDIS_PORT, redis_db=0):
        self.redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)
        self.driver = self._init_driver()
        self.logger = self._init_logger()
    
    def _init_driver(self):
        options = webdriver.ChromeOptions()
        try:
            ua = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0"
        except FakeUserAgentError:
            ua = UserAgent().chrome
        options.add_argument(f'user-agent={ua}')
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
    
    def _extract_avito_id(self, url: str) -> str | None:
        match = re.search(r'(\d+)(?=\?)', url)  # Ищем число перед ?
        if not match:
            match = re.search(r'(\d+)$', url)  # Ищем число в конце строки
        return match.group(1) if match else None
    
    def _human_delay(self, min_time=2, max_time=5):
        time.sleep(random.uniform(min_time, max_time))
        
    def _human_mouse(self, min_time=2, max_time=5):
        actions = ActionChains(self.driver)
        
        # Найдем элемент на странице, к которому будем перемещать мышь
        submit_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-marker='search-form/submit-button']"))
        )
        
        for _ in range(random.randint(min_time, max_time)):
            # Генерация случайных смещений
            offset_x = random.randint(10, 50)
            offset_y = random.randint(10, 50)
            
            # Перемещение курсора в случайное место относительно элемента body
            actions.move_to_element_with_offset(submit_button, offset_x, offset_y).perform()
            
            # Скроллинг страницы
            self.driver.execute_script("window.scrollBy(0, arguments[0]);", random.randint(100, 300))
            self.logger.info("Scrolling")
            
            self._human_delay(0.2, 0.7)  # Небольшая задержка


    
    def _parse_ads(self):
        ads = self.driver.find_elements(By.CSS_SELECTOR, "div[data-marker='item']")
        new_ads = []
        
        for ad in ads[:10]:
            try:
                link = ad.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                ad_id = self._extract_avito_id(link)
                self.logger.info(f"Processing ad {ad_id}")
                if not self.redis_client.exists(f"{ad_id}"):
                    title = ad.find_element(By.CSS_SELECTOR, "h3").text
                    price = ad.find_element(By.CSS_SELECTOR, "p[data-marker='item-price'] span").text
                    city = ad.find_element(By.CSS_SELECTOR, "div[class^='geo-root-NrkbV'] p span").text
                    new_ads.append({'title': title, 'price': price, 'link': link, 'city': city})
            except Exception as ex:
                self.logger.error(f"Error processing ad: {ex}")
                continue
        
        self.logger.info(f"Found {len(new_ads)} new ads")
        self._human_mouse(2, 5)

        return new_ads
    
    def _parse_characteristics(self):
        characteristics = {}
        exclude_values = {"Проверить в Автотеке", "Неизвестно", "Нет данных"}

        try:
            li_elements = self.driver.find_elements(By.CSS_SELECTOR, "li[class^='params-paramsList__item']")
            
            for li in li_elements:
                try:
                    spans = li.find_elements(By.TAG_NAME, "span")
                    
                    if spans:
                        key = spans[0].text.strip().replace(":", "")
                        
                        # Удаляем текст первого <span> из общего текста <li>
                        full_text = li.text.strip()
                        value = full_text.replace(spans[0].text, "").strip(":").strip()

                        if key and value and value not in exclude_values:
                            characteristics[key] = value
                        else:
                            print(f"⚠️ Проблема с разбором: {li.get_attribute('outerHTML')}")

                except Exception as e:
                    print(f"❌ Ошибка при обработке {li.get_attribute('outerHTML')}: {e}")

        except Exception as e:
            print(f"❌ Ошибка при парсинге характеристик: {e}")

        return characteristics

    def _extract_brand_model(self, title: str):
        # Разбиваем строку по запятой (удаляем пробег и год)
        main_part = title.split(",")[0]

        # Проверяем, есть ли скобки в начале (например, "ВАЗ (LADA)")
        match = re.match(r"^([\w-]+(?:\s*\([\w\s-]+\))?)\s+(.+)", main_part)
        
        if match:
            brand = match.group(1)  # Бренд (учитывает скобки)
            model = match.group(2)  # Все остальное — модель
            return brand, model
        return None, None

    def _normalize_car_data(self, raw_data: dict) -> dict:
        """
        Приводит данные автомобиля к стандартному формату.
        """
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
            "year": __normalize_int(raw_data.get("year"), default=1900),
            "image": raw_data.get("image", ""),
            "price": __normalize_int(raw_data.get("price"), default=0),
            "city": __normalize_str(raw_data.get("city")),
            "brand": __normalize_str(raw_data.get("brand")),
            "model": __normalize_str(raw_data.get("model")),
            "mileage": __normalize_int(raw_data.get("mileage"), default=0),
            "engine": __normalize_str(raw_data.get("engine")),
            "color": __normalize_str(raw_data.get("color")),
            "gearbox": __normalize_str(raw_data.get("gearbox")),
            "drive":__normalize_str(raw_data.get("drive")),
            "steering": __normalize_str(raw_data.get("steering")),
            "owners": min(__normalize_int(raw_data.get("owners"), default=0), 99),
            "body_type": __normalize_str(raw_data.get("body_type")),
            "condition": __normalize_str(raw_data.get("condition")),
            "ad_type": ad_type_mapping.get(__normalize_str(raw_data.get("ad_type")), "unknown"),
            "seller": seller_mapping.get(__normalize_str(raw_data.get("seller")), "unknown")
        }
    
    def _parse_details(self, ad):
        self.driver.get(ad['link'])
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "img")))
        self._human_mouse(1, 2)
        self._human_delay(1, 3)

        
        try:            
            brand, model = self._extract_brand_model(ad['title'])
            characteristics = self._parse_characteristics()
            # Парсинг деталей
            image = self.driver.find_element(By.CSS_SELECTOR, "img").get_attribute("src")
            details = {
                "platform" : "avito",
                "link": ad['link'],
                "name": ad['title'],
                "year": characteristics.get('Год выпуска'),
                "image": image,
                "price": ad['price'],
                "city": ad['city'],
                
                # Бренд и модель 
                "brand": brand,
                "model": model,
                
                # Характеристики
                "mileage": characteristics.get('Пробег'),
                "engine": characteristics.get('Тип двигателя'),
                "color": characteristics.get('Цвет'),
                "gearbox": characteristics.get('Коробка передач'),
                "drive": characteristics.get('Привод'),
                "steering": characteristics.get('Руль'),
                "owners": characteristics.get('Владельцев по ПТС'),
                "body_type": characteristics.get('Тип кузова'),
                "condition": characteristics.get('Состояние'),
                
                # Тип объявления и продавец
                "ad_type": None,
                "seller": self.driver.find_element(By.CSS_SELECTOR, "div[data-marker^='seller-info/label'").text,
            }
            ad_id = self._extract_avito_id(ad['link'])
            normalized_details = self._normalize_car_data(details)
            self.redis_client.setex(f"{ad_id}", 1800, json.dumps(normalized_details, ensure_ascii=False))  # Сохранение объявления в Redis
            self.logger.info(f"Saved ad {ad_id} to Redis")
            return normalized_details
        except Exception as ex:
            self.logger.error(f"Error parsing ad details: {ex}")
        
        return None
    
    
    def parse(self):
        try:
            while True:
                self.driver.delete_all_cookies()
                url = "https://www.avito.ru/all/avtomobili?s=104"
                self.logger.info("Opening avito.ru")
                self.driver.get(url)
                self.driver.implicitly_wait(10)  # Делаем ожидания для загрузки элементов
                self.logger.info("Opened avito.ru")
                self._human_mouse(1, 2)
                self._human_delay()
                
                # Ожидание появления объявлений
                try:
                    WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-marker='item']"))
                    )
                    self.logger.info("Объявления загружены, начинаем парсинг")
                except Exception as e:
                    self.logger.error(f"Ошибка ожидания объявлений: {e}")
                    return  # Можно выйти из метода, если объявления так и не загрузились
                
                new_ads = self._parse_ads()
                
                # Парсинг деталей
                if new_ads:
                    count = 0
                    for ad in new_ads:
                        try:
                            count += 1
                            self.logger.info(f"Processing ad {count}/{len(new_ads)}")
                            details = self._parse_details(ad)
                            if details:
                                self.logger.info(f"New ad: {details}")
                            self._human_delay(2, 5)
                        except Exception as ex:
                            self.logger.error(f"Error processing ad: {ex}")
                            continue
                else:
                    self.logger.info("No new ads found.")
                    self._human_delay(5, 10) # дополнительная задержка после отсутствия новых объявлений
                
                self._human_delay(5, 10)
                
        except Exception as ex:
            # При ошибке выход на 5 минут, после - повторный запуск
            self.logger.error(f"Unhandled error: {ex} \n It may be block IP or something else. \n Restarting in 5 minutes")
            self.driver.quit()
            self._human_delay(300, 350)
            self.parse()
        finally:
            self.logger.info("Driver closed")

if __name__ == '__main__':
    parser = AvitoParser()
    parser.parse()
