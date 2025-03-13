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
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from fake_useragent import UserAgent, FakeUserAgentError

class DromParser:
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
    
    def _extract_drom_id(self, url: str) -> str | None:
        match = re.search(r'/(\d+).html', url)  # Ищем число перед ?
        if not match:
            match = re.search(r'(\d+)$', url)  # Ищем число в конце строки
        return match.group(1) if match else None
    
    def _extract_info(self, url: str) -> str | None:
        pattern = r'https://auto.drom.ru/([^/]+)/([^/]+)/([^/]+)/\d+.html'
        match = re.match(pattern, url)
        if match:
            city, brand, model = match.groups()
            return [city, brand, model]
        return None
    
    def _human_delay(self, min_time=2, max_time=5):
        time.sleep(random.uniform(min_time, max_time))
        
    def _human_mouse(self, min_time=2, max_time=5):
        actions = ActionChains(self.driver)
        
        # Найдем элемент на странице, к которому будем перемещать мышь
        submit_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[data-ftid='component_header_add-bull']"))
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
        ads = self.driver.find_elements(By.CSS_SELECTOR, "div[data-ftid='bulls-list_bull']")
        new_ads = []
        
        for ad in ads[:10]:
            try:
                link = ad.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                ad_id = self._extract_drom_id(link)
                self.logger.info(f"Processing ad {ad_id}")
                if not self.redis_client.exists(f"{ad_id}"):
                    title = ad.find_element(By.CSS_SELECTOR, "h3").text
                    price = ad.find_element(By.CSS_SELECTOR, "span[class='css-46itwz e162wx9x0']").text
                    new_ads.append({'title': title, 'price': price, 'link': link})
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
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table[class^='css-xalqz7']"))
            )
            self.logger.info("Таблица загружена, начинаем обработку строк...")
            # Получаем все строки таблицы
            tr_elements = self.driver.find_elements(By.CSS_SELECTOR, "table[class^='css-xalqz7'] tbody tr")

            # Теперь обрабатываем строки
            for tr in tr_elements:
                try:
                    key_element = tr.find_elements(By.TAG_NAME, "th")
                    value_element = tr.find_elements(By.TAG_NAME, "td")

                    if key_element and value_element:
                        key = key_element[0].text.strip()  # Извлекаем ключ
                        if not key:
                            self.logger.info(f"Пропускаем строку с пустым ключом: {tr.get_attribute('outerHTML')}")
                            continue
                        value = value_element[0].text.strip()  # Извлекаем значение
                        if value:
                            # Исключаем значения из списка exclude_values
                            if value not in exclude_values:
                                characteristics[key] = value
                            else:
                                self.logger.info(f"Исключаем значение: {key} = {value}")
                        else:
                            self.logger.info(f"Пустое значение для {key}")
                    else:
                        self.logger.info(f"Не найдено элементов key или value в строке: {tr.get_attribute('outerHTML')}")

                except Exception as e:
                    self.logger.error(f"Ошибка при обработке строки: {tr.get_attribute('outerHTML')}, ошибка: {e}")

        except Exception as e:
            self.logger.error(f"Ошибка при парсинге характеристик: {e}")

        self.logger.debug("Завершение парсинга характеристик.")
        return characteristics


    def _parse_details(self, ad):
        self.driver.get(ad['link'])
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "img")))
        self._human_mouse(1, 2)
        self._human_delay(1, 3)
        
        
        try:
            # Парсинг деталей
            image = self.driver.find_element(By.CSS_SELECTOR, "img[class='css-qy78xy evrha4s0']").get_attribute("src")
            extracted_info = self._extract_info(ad['link'])
            title = ad.get('title', '')  # Получаем заголовок, если его нет — пустая строка
            title_parts = title.rsplit(", ", 1)  # Разделяем строку по последней запятой
            characteristics = self._parse_characteristics()
            details = {
                "platform" : "drom",
                "link": ad['link'],
                "name": title_parts[0] if len(title_parts) > 1 else title,  # Если есть запятая — берем до нее, иначе весь title
                "year": title_parts[1] if len(title_parts) > 1 else None,   # Если нет запятой — год не указан
                "image": image,
                "price": ad['price'],
                "city": extracted_info[0] if extracted_info else None,
                
                # Бренд и модель
                "brand": extracted_info[1] if extracted_info else None,
                "model": extracted_info[2] if extracted_info else None,
                
                # Характеристики
                "engine": characteristics.get('Двигатель'),
                "mileage": characteristics.get('Пробег'),
                "color": characteristics.get('Цвет'),
                "gearbox": characteristics.get('Коробка передач'),
                "drivetrain": characteristics.get('Привод'),
                "steering": characteristics.get('Руль'),
                "owners": characteristics.get('Владельцы'),
                "body_type": characteristics.get('Тип кузова'),
                
                # Дополнительные поля
                "condition": None,
                "ad_type": None,
                "seller": None,
            }
            ad_id = self._extract_drom_id(ad['link'])
            self.redis_client.setex(f"{ad_id}", 1800, json.dumps(details, ensure_ascii=False))  # Сохранение объявления в Redis
            self.logger.info(f"Saved ad {ad_id} to Redis")
            return details
        except Exception as ex:
            self.logger.error(f"Error parsing ad details: {ex}")
        
        return None
    
    
    def parse(self):
        try:
            while True:
                self.driver.delete_all_cookies()
                url = "https://auto.drom.ru/all/"
                self.logger.info("Opening drom.ru")
                self.driver.get(url)
                self.driver.implicitly_wait(10)  # Делаем ожидания для загрузки элементов
                self.logger.info("Opened drom.ru")
                self._human_mouse(1, 2)
                self._human_delay()
                
                # Ожидание появления объявлений
                try:
                    WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-ftid='bulls-list_bull']"))
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
    parser = DromParser()
    parser.parse()
