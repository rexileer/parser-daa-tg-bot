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

class AutoruParser:
    def __init__(self, filters=None, redis_host='localhost', redis_port=6379, redis_db=0):
        self.filters = filters or {}
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
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(1)
        return driver
    
    def _init_logger(self):
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(__name__)
    
    def _extract_autoru_id(self, url: str) -> str | None:
        match = re.search(r'/(\d+)-\w+/', url)
        if not match:
            match = re.search(r'(\d+)$', url)  # Ищем число в конце строки
        return match.group(1) if match else None
    
    def _human_delay(self, min_time=2, max_time=5):
        time.sleep(random.uniform(min_time, max_time))
        
    def _human_mouse(self, min_time=2, max_time=5):
        actions = ActionChains(self.driver)
        
        # Найдем элемент на странице, к которому будем перемещать мышь
        submit_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "li[data-id='history']"))
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
                    if item:
                        key = item[0].text
                        value = item[1].text
                        if key and value and value not in exclude_values:
                            characteristics[key] = value
                        else:
                            print(f"⚠️ Проблема с разбором: {li.get_attribute('outerHTML')}")
                except Exception as e:
                    print(f"❌ Ошибка при обработке {li.get_attribute('outerHTML')}: {e}")
        except Exception as e:
            print(f"❌ Ошибка при парсинге характеристик: {e}")
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
                    
                    # Ищем возможные элементы значения
                    value_elements = li.find_elements(By.CSS_SELECTOR, "div[class^='CardInfoGroupedRow__cellValue'], span, a")
                    
                    # Собираем текст из всех найденных элементов
                    values = [el.text.strip() for el in value_elements if el.text.strip()]
                    value = " / ".join(values) if values else None  # Объединяем, если несколько
                    if key and value and value not in exclude_values:
                        characteristics[key] = value
                    else:
                        print(f"⚠️ Проблема с разбором: {li.get_attribute('outerHTML')}")
                except Exception as e:
                    print(f"❌ Ошибка при обработке {li.get_attribute('outerHTML')}: {e}")
        except Exception as e:
            print(f"❌ Ошибка при парсинге характеристик: {e}")
        return characteristics
    
    
    def _extract_info(self, url: str) -> str | None:
        pattern = r'https://auto.ru/cars/(new/group|used/sale)/([^/]+)/([^/]+)/'
        match = re.match(pattern, url)
        if match:
            type, brand, model = match.groups()
            return [type, brand, model]
        return None
    
    
    def _parse_details(self, ad):
        self.driver.get(ad['link'])
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "img")))
        self._human_mouse(1, 2)
        self._human_delay(1, 3)

        
        try:
            extracted_info = self._extract_info(ad['link'])
            if not extracted_info:
                self.logger.error(f"Failed to extract info from URL: {ad['link']}")
                return
            elif extracted_info[0] == "used/sale":
                characteristics = self._parse_characteristics()
            else:
                characteristics = self._parse_characteristics_new()
            title = self.driver.find_element(By.CSS_SELECTOR, "h1").text  # Получаем заголовок, если его нет — пустая строка
            title_parts = title.rsplit(", ", 1)  # Разделяем строку по последней запятой
            # Парсинг деталей
            details = {
                "platform" : "autoru",
                "link": ad['link'],
                "name": title_parts[0] if len(title_parts) > 1 else title,
                "year": title_parts[1] if len(title_parts) > 1 else None,
                "image": self.driver.find_element(By.CSS_SELECTOR, "img[class='ImageGalleryDesktop__image']").get_attribute("src"),
                "price": self.driver.find_element(By.CSS_SELECTOR, "span[class='OfferPriceCaption__price']").text,
                "city": self.driver.find_element(By.CSS_SELECTOR, "div[class^='CardSellerNamePlace2__address'] span[class^='MetroListPlace__regionName']").text,
                
                # Бренд и модель 
                "brand": extracted_info[1] if extracted_info else None,
                "model": extracted_info[2] if extracted_info else None,
                
                # Характеристики
                "mileage": characteristics.get('Пробег'),
                "engine": characteristics.get('Двигатель'),
                "color": characteristics.get('Цвет'),
                "gearbox": characteristics.get('Коробка'),
                "drivetrain": characteristics.get('Привод'),
                "steering": characteristics.get('Руль'),
                "owners": characteristics.get('Владельцы'),
                "body_type": characteristics.get('Кузов'),
                "condition": characteristics.get('Состояние'),
                
                # Тип объявления и продавец
                "ad_type": "new" if extracted_info and extracted_info[0] == "new/group" else "used",
                "seller": "group" if extracted_info and extracted_info[0] == "new/group" else "private",
            }
            ad_id = self._extract_autoru_id(ad['link'])
            self.redis_client.setex(f"{ad_id}", 1800, json.dumps(details, ensure_ascii=False))  # Сохранение объявления в Redis
            self.logger.info(f"Saved ad {ad_id} to Redis")
            return details
        except Exception as ex:
            self.logger.error(f"Error parsing ad details: {ex}")
        
        return None
    
    
    def _cookies_accept(self):
        try:
            accept_cookies = self.driver.find_element(By.CSS_SELECTOR, "a[id='confirm-button']")
            accept_cookies.click()
            self.logger.info("Cookies accepted")
        except Exception as e:
            self.logger.info(f"Not able to accepting cookies")
    
    def parse(self):
        try:
            while True:
                url = "https://auto.ru/rossiya/cars/all/?sort=cr_date-desc"
                self.logger.info("Opening auto.ru")
                self.driver.get(url)
                self.driver.implicitly_wait(10)  # Делаем ожидания для загрузки элементов
                self.logger.info("Opened auto.ru")
                self._cookies_accept()
                self._human_delay()
                self._human_mouse(1, 2)
                
                # Ожидание появления объявлений
                try:
                    WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div[class='ListingItem']"))
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
                            # self._human_delay(2, 5)
                        except Exception as ex:
                            self.logger.error(f"Error processing ad: {ex}")
                            continue
                else:
                    self.logger.info("No new ads found.")
                    self._human_delay(5, 10) # дополнительная задержка после отсутствия новых объявлений
                
                self._human_delay(5, 10)
                # self.driver.delete_all_cookies()  # Очистить cookies после каждого запроса
                
                        
        except Exception as ex:
            # При ошибке выход на 5 минут, после - повторный запуск
            self.logger.error(f"Unhandled error: {ex} \n It may be block IP or something else. \n Restarting in 5 minutes")
            self.driver.quit()
            self._human_delay(300, 350)
            self.parse()
        finally:
            self.logger.info("Driver closed")

if __name__ == '__main__':
    parser = AutoruParser()
    parser.parse()
