import json
import time
import random
import re
import logging
import redis
import os
import shutil
import pickle
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD

class AutoruParser:
    def __init__(self, filters=None, redis_host=REDIS_HOST, redis_port=REDIS_PORT, redis_db=0, max_screenshots=20, max_screenshot_dirs=10, redis_password=REDIS_PASSWORD):
        self.filters = filters or {}
        self.redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, password=redis_password, decode_responses=True)
        self.driver = self._init_driver()
        self.logger = self._init_logger()
        self.screenshot_dir = self._init_screenshot_dir()
        self.screenshot_count = 0
        self.max_screenshots = max_screenshots  # Максимальное число скриншотов за одну итерацию
        self.max_screenshot_dirs = max_screenshot_dirs  # Максимальное количество директорий со скриншотами
        self._cleanup_old_screenshots()
    
    def _init_driver(self):
        options = webdriver.ChromeOptions()
        # Используем более современный и распространенный user-agent
        desktop_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        options.add_argument(f'user-agent={desktop_ua}')
        
        # Базовые настройки
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # Улучшенная маскировка автоматизации
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Реалистичное разрешение экрана
        options.add_argument('--window-size=1920,1080')
        
        # Включаем JavaScript и изображения для более естественного поведения
        options.add_argument('--enable-javascript')
        
        # Отключаем некоторые оптимизации для более стабильной работы
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-client-side-phishing-detection")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-renderer-backgrounding")
        
        # Отключаем режим инкогнито для сохранения cookies
        # options.add_argument('--incognito')
        
        driver = webdriver.Remote(
            command_executor="http://chrome_driver:4444/wd/hub",
            options=options,
        )
        
        # Скрываем факт использования WebDriver с помощью JavaScript
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Случайное время ожидания для имитации человеческого поведения
        driver.implicitly_wait(random.uniform(3, 7))
        
        return driver
    
    def _save_cookies(self):
        """Сохраняет cookies текущей сессии"""
        try:
            with open('autoru_cookies.pkl', 'wb') as file:
                pickle.dump(self.driver.get_cookies(), file)
            self.logger.info("Cookies успешно сохранены")
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении cookies: {e}")

    def _load_cookies(self):
        """Загружает сохраненные cookies"""
        try:
            if os.path.exists('autoru_cookies.pkl'):
                with open('autoru_cookies.pkl', 'rb') as file:
                    cookies = pickle.load(file)
                    # Сначала нужно открыть сайт, чтобы установить домен для cookies
                    self.driver.get("https://auto.ru")
                    time.sleep(2)
                    for cookie in cookies:
                        try:
                            self.driver.add_cookie(cookie)
                        except:
                            pass
                self.logger.info("Cookies успешно загружены")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке cookies: {e}")
            return False
    
    def _human_behavior(self):
        """Имитирует человеческое поведение на странице (не более 3 секунд)"""
        try:
            # Короткая задержка
            time.sleep(random.uniform(0.3, 0.7))
            
            # Простой скролл страницы (не требует поиска элементов)
            scroll_height = random.randint(100, 300)
            self.driver.execute_script(f"window.scrollTo(0, {scroll_height});")
            
            # Используем JavaScript для наведения на случайные элементы без риска stale reference
            self.driver.execute_script("""
                var elements = document.querySelectorAll('a, button');
                if (elements.length > 0) {
                    var randomElement = elements[Math.floor(Math.random() * elements.length)];
                    if (randomElement) {
                        randomElement.scrollIntoView({behavior: 'smooth', block: 'center'});
                    }
                }
            """)
            
            # Короткая задержка в конце
            time.sleep(random.uniform(0.3, 0.7))
        except Exception as e:
            self.logger.warning(f"Ошибка при имитации поведения: {e}")
            # Продолжаем выполнение даже при ошибках
    
    def _init_logger(self):
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger("autoru_parser")
    
    def _cleanup_old_screenshots(self):
        """Удаляет старые директории со скриншотами, оставляя только последние N директорий"""
        try:
            base_dir = "screenshots/autoru"
            if not os.path.exists(base_dir):
                os.makedirs(base_dir, exist_ok=True)
                return
                
            # Получаем все директории со скриншотами
            dirs = []
            for item in os.listdir(base_dir):
                item_path = os.path.join(base_dir, item)
                if os.path.isdir(item_path):
                    # Получаем время модификации директории
                    dirs.append((item_path, os.path.getmtime(item_path)))
            
            # Сортируем по времени (от старых к новым)
            dirs.sort(key=lambda x: x[1])
            
            # Удаляем старые директории, если их больше чем max_screenshot_dirs
            if len(dirs) > self.max_screenshot_dirs:
                for dir_path, _ in dirs[:-self.max_screenshot_dirs]:
                    self.logger.info(f"Удаляем старую директорию со скриншотами: {dir_path}")
                    shutil.rmtree(dir_path, ignore_errors=True)
        except Exception as e:
            self.logger.error(f"Ошибка при очистке старых скриншотов: {e}")
    
    def _init_screenshot_dir(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        directory = f"screenshots/autoru/main_loop_{timestamp}"
        os.makedirs(directory, exist_ok=True)
        return directory
        
    def _take_screenshot(self, prefix="debug"):
        """Take a screenshot and save it with timestamp for debugging"""
        # Проверяем, не превышен ли лимит скриншотов
        if self.screenshot_count >= self.max_screenshots:
            self.logger.info(f"Достигнут лимит скриншотов ({self.max_screenshots}), пропускаем создание")
            return None
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.screenshot_dir}/{prefix}_{timestamp}.png"
        try:
            self.driver.save_screenshot(filename)
            self.screenshot_count += 1
            self.logger.info(f"Screenshot saved to {filename} ({self.screenshot_count}/{self.max_screenshots})")
            return filename
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {e}")
            return None
    
    def _extract_autoru_id(self, url: str) -> str | None:
        match = re.search(r'/(\d+)-\w+/', url)
        if not match:
            match = re.search(r'(\d+)$', url)
        return match.group(1) if match else None
    
    def _human_delay(self, min_time=2, max_time=5):
        time.sleep(random.uniform(min_time, max_time))
    
    def _check_for_captcha(self):
        """Check if a CAPTCHA is present on the page - быстрая проверка через JavaScript"""
        try:
            # Используем JavaScript для быстрой проверки без ожидания
            captcha_detected = self.driver.execute_script("""
                const pageText = document.body.innerText.toLowerCase();
                return pageText.includes('captcha') || 
                       pageText.includes('recaptcha') || 
                       pageText.includes('hcaptcha') ||
                       !!document.querySelector('iframe[src*="captcha"]');
            """)
            
            if captcha_detected:
                self._take_screenshot("captcha_detected")
                self.logger.warning("CAPTCHA detected on the page")
                return True
                
            return False
        except Exception as e:
            self.logger.error(f"Error checking for CAPTCHA: {e}")
            return False
    
    def _check_for_block(self):
        """Check if we've been blocked or restricted - быстрая проверка через JavaScript"""
        try:
            # Используем JavaScript для быстрой проверки без ожидания
            block_detected = self.driver.execute_script("""
                const pageText = document.body.innerText.toLowerCase();
                return pageText.includes('доступ ограничен') || 
                       pageText.includes('заблокирован') || 
                       pageText.includes('подозрительная активность') ||
                       pageText.includes('временно недоступен');
            """)
            
            if block_detected:
                self._take_screenshot("access_blocked")
                self.logger.warning("Access potentially blocked")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error checking for blocks: {e}")
            return False
        
    def _parse_ads(self):
        try:
            # Уменьшаем неявное ожидание для ускорения
            self.driver.implicitly_wait(1)
            
            # Используем более быстрый поиск элементов
            ads = WebDriverWait(self.driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[data-seo='listing-item'], div.ListingItem"))
            )
            
            self.logger.info(f"Найдено {len(ads)} объявлений на странице")
            new_ads = []
            
            # Собираем все ссылки и ID сразу, без обработки каждого элемента отдельно
            for ad in ads[:10]:
                try:
                    link_element = WebDriverWait(ad, 1).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "a"))
                    )
                    link = link_element.get_attribute("href")
                    ad_id = self._extract_autoru_id(link)
                    
                    # Быстрая проверка на тип объявления
                    ad_type = "обычное"
                    try:
                        if ad.find_elements(By.CSS_SELECTOR, "div[class*='ListingItemServices']"):
                            ad_type = "продвижение"
                    except:
                        pass
                    
                    self.logger.info(f"Processing ad {ad_id}")
                    
                    # Проверяем наличие в Redis без блокировки
                    if not self.redis_client.exists(f"{ad_id}"):
                        new_ads.append({'link': link, 'ad_type': ad_type, 'ad_id': ad_id})
                except Exception as ex:
                    self.logger.error(f"Error processing ad: {ex}")
                    continue
                
            self.logger.info(f"Found {len(new_ads)} new ads")
            return new_ads
        finally:
            # Восстанавливаем стандартное неявное ожидание
            self.driver.implicitly_wait(3)
    
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
            "gearbox": "механика" if __normalize_str(raw_data.get("gearbox")) == "механическая" else __normalize_str(raw_data.get("gearbox")),
            "drive": __normalize_str(raw_data.get("drive")),
            "steering": __normalize_str(raw_data.get("steering")),
            "owners": __normalize_int(raw_data.get("owners"), default="unknown"),
            "body_type": __normalize_str(raw_data.get("body_type")),
            "condition": "не битый" if __normalize_str(raw_data.get("condition")) == "не требует ремонта" else __normalize_str(raw_data.get("condition")),
            "ad_type": __normalize_str(raw_data.get("ad_type")),
            "seller": __normalize_str(raw_data.get("seller")),
        }
    
    def _parse_details(self, ad):
        try:
            # Устанавливаем короткое неявное ожидание для ускорения
            self.driver.implicitly_wait(2)
            self.driver.get(ad['link'])
            
            # Используем короткое явное ожидание с таймаутом 5 секунд вместо 10
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h1, img.ImageGalleryDesktop__image"))
                )
            except Exception as e:
                self.logger.error(f"Ошибка ожидания загрузки страницы: {e}")
                self._take_screenshot("page_loading_error")
                return None
            
            # Уменьшаем задержку
            time.sleep(random.uniform(0.5, 1.0))
            
            extracted_info = self._extract_info(ad['link'])
            if not extracted_info:
                self.logger.error(f"Не удалось извлечь информацию из URL: {ad['link']}")
                return None
            
            # Если тип объявления "new/group", используем новые характеристики
            characteristics = self._parse_characteristics_new() if extracted_info[0] == "new/group" else self._parse_characteristics()
            
            # Собираем все данные через одну функцию с обработкой ошибок
            def get_element_safely(selector, attribute=None, default=""):
                try:
                    element = WebDriverWait(self.driver, 1).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if attribute:
                        return element.get_attribute(attribute)
                    return element.text
                except:
                    return default
            
            # Парсинг картинки и заголовка
            image = get_element_safely("img.ImageGalleryDesktop__image", "src")
            title = get_element_safely("h1")
            title_parts = title.rsplit(", ", 1)
            
            # Сборка деталей
            details = {
                "platform": "autoru",
                "link": ad['link'],
                "name": title_parts[0] if len(title_parts) > 1 else title,
                "year": title_parts[1] if len(title_parts) > 1 else None,
                "image": image,
                "price": get_element_safely("span.OfferPriceCaption__price"),
                "city": get_element_safely("div[class^='CardSellerNamePlace2__address'] span[class^='MetroListPlace__regionName']"),
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
                "ad_type": ad['ad_type'],
                "seller": "автодилер" if extracted_info and extracted_info[0] == "new/group" else "частное лицо",
            }
            
            ad_id = self._extract_autoru_id(ad['link'])
            normalized_details = self._normalize_car_data(details)
            self.redis_client.setex(f"{ad_id}", 1800, json.dumps(normalized_details, ensure_ascii=False))
            self.logger.info(f"Saved ad {ad_id} to Redis")
            return normalized_details
            
        except Exception as ex:
            self.logger.error(f"Error parsing ad details: {ex}")
            self._take_screenshot("detail_parsing_error")
            return None
        finally:
            # Восстанавливаем стандартное неявное ожидание
            self.driver.implicitly_wait(3)
    
    def _cookies_accept(self):
        try:
            # Уменьшаем время ожидания до 0.5 секунды
            self.driver.implicitly_wait(0.5)
            
            # Быстрая проверка наличия кнопки принятия cookies через JavaScript
            cookie_button_exists = self.driver.execute_script("""
                return !!document.querySelector("a#confirm-button");
            """)
            
            if cookie_button_exists:
                # Если кнопка есть, кликаем по ней через JavaScript для мгновенного действия
                self.driver.execute_script("""
                    const button = document.querySelector("a#confirm-button");
                    if (button) button.click();
                """)
                self.logger.info("Cookies accepted via JavaScript")
                return True
            else:
                self.logger.info("Кнопка принятия cookies не найдена")
                return False
        except Exception as e:
            self.logger.info("Не удалось принять cookies, возможно их нет на странице.")
            return False
        finally:
            # Восстанавливаем стандартное ожидание
            self.driver.implicitly_wait(3)
    
    def parse(self):
        consecutive_errors = 0
        max_consecutive_errors = 3
        
        while True:
            try:
                # Initialize a new screenshot directory for each iteration
                self.screenshot_dir = self._init_screenshot_dir()
                self.screenshot_count = 0  # Сбрасываем счетчик скриншотов
                self._cleanup_old_screenshots()  # Очищаем старые директории
                
                # Пытаемся загрузить cookies, если они есть
                cookies_loaded = self._load_cookies()
                
                url = "https://auto.ru/rossiya/cars/all/?sort=cr_date-desc"
                self.logger.info("Opening auto.ru")
                self.driver.get(url)
                self.driver.implicitly_wait(10)
                self.logger.info("Opened auto.ru")
                
                # Имитируем человеческое поведение
                self._human_behavior()
                
                self.logger.info("Имитация человеческого поведения прошла")
                
                # Принимаем cookies сразу после загрузки страницы, до скриншота
                self._cookies_accept()
                
                # Take a screenshot to see what's on the page
                self._take_screenshot("initial_page")
                
                # Быстрая проверка CAPTCHA и блокировки
                if self._check_for_captcha() or self._check_for_block():
                    self.logger.error("Detected CAPTCHA or access restriction. Waiting before retry...")
                    self._human_delay(300, 360)  # Wait longer if blocked
                    consecutive_errors += 1
                    if consecutive_errors >= max_consecutive_errors:
                        self.logger.error(f"Reached {max_consecutive_errors} consecutive errors. Reinitializing driver...")
                        self.driver.quit()
                        self.driver = self._init_driver()
                        consecutive_errors = 0
                    continue
                
                # Try to find listing items with better error handling
                try:
                    # First, check if page loaded at all
                    WebDriverWait(self.driver, 20).until(
                        EC.visibility_of_element_located((By.TAG_NAME, "body"))
                    )
                    
                    # Take screenshot of the page content
                    self._take_screenshot("before_listings_wait")
                    
                    # Имитируем человеческое поведение перед поиском объявлений
                    self._human_behavior()
                    
                    # Try to find different ad container selectors (site might change)
                    selectors = [
                        "div[class='ListingItem']", 
                        "div[data-seo='listing-item']",
                        "div[class*='listing']"
                    ]
                    
                    # Try each selector
                    found = False
                    for selector in selectors:
                        try:
                            self.logger.info(f"Trying selector: {selector}")
                            WebDriverWait(self.driver, 30).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                            )
                            self.logger.info(f"Found elements with selector: {selector}")
                            found = True
                            break
                        except Exception as e:
                            self.logger.warning(f"Selector {selector} failed: {e}")
                    
                    if not found:
                        raise Exception("No listings found with any known selectors")
                        
                    self.logger.info("Объявления загружены, начинаем парсинг")
                    
                except Exception as e:
                    self._take_screenshot("waiting_error")
                    self.logger.error(f"Ошибка ожидания объявлений: {e}")
                    
                    # Get page source for debugging
                    try:
                        page_source = self.driver.page_source
                        self.logger.info(f"Page title: {self.driver.title}")
                        self.logger.info(f"Page source length: {len(page_source)}")
                        # Сохраняем исходный код только если количество скриншотов не превышено
                        if self.screenshot_count < self.max_screenshots:
                            with open(f"{self.screenshot_dir}/page_source.html", "w", encoding="utf-8") as f:
                                f.write(page_source)
                            self.screenshot_count += 1
                    except Exception as ps_error:
                        self.logger.error(f"Failed to save page source: {ps_error}")
                    
                    consecutive_errors += 1
                    if consecutive_errors >= max_consecutive_errors:
                        self.logger.error(f"Reached {max_consecutive_errors} consecutive errors. Reinitializing driver...")
                        self.driver.quit()
                        self.driver = self._init_driver()
                        consecutive_errors = 0
                    
                    self._human_delay(15, 30)  # Wait longer between retries
                    continue
                
                # Reset consecutive errors counter on success
                consecutive_errors = 0
                
                new_ads = self._parse_ads()
                if new_ads:
                    count = 0
                    # Create a new directory for ad details screenshots only if we have new ads
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    ads_dir = f"screenshots/autoru/load_ads_{timestamp}"
                    os.makedirs(ads_dir, exist_ok=True)
                    
                    # Ограничиваем количество обрабатываемых объявлений
                    max_ads_to_process = min(len(new_ads), 10)  # Обрабатываем максимум 10 объявлений
                    
                    # Предварительно загружаем все объявления в список для параллельной обработки
                    ads_to_process = new_ads[:max_ads_to_process]
                    
                    # Обработка объявлений с минимальными задержками
                    for ad in ads_to_process:
                        try:
                            count += 1
                            # Используем ad_id из предварительно собранных данных
                            ad_id = ad.get('ad_id', self._extract_autoru_id(ad['link']))
                            self.logger.info(f"Processing ad details {count}/{max_ads_to_process} (ID: {ad_id})")
                            
                            # Set temporary screenshot dir for this ad
                            temp_dir = self.screenshot_dir
                            self.screenshot_dir = ads_dir
                            self.screenshot_count = 0  # Сбрасываем счетчик для каждого объявления
                            
                            # Обрабатываем объявление с минимальной задержкой
                            details = self._parse_details(ad)
                            self.screenshot_dir = temp_dir  # Restore main screenshot dir
                            
                            # Минимальная задержка между объявлениями
                            time.sleep(random.uniform(0.3, 0.7))
                            
                            if details:
                                self.logger.info(f"Saved ad: {ad_id}")
                        except Exception as ex:
                            self.logger.error(f"Error processing ad: {ex}")
                            continue
                else:
                    self.logger.info("No new ads found.")
                    self._human_delay(10, 15)
                
                # Сохраняем cookies после успешного парсинга
                self._save_cookies()
                
                # Longer delay between main parsing cycles
                self._human_delay(15, 30)
            
            except Exception as ex:
                self.logger.error(f"Unhandled error: {ex} \n Возможна блокировка IP или другая ошибка. Перезапуск через 5 минут.")
                self._take_screenshot("unhandled_error")
                consecutive_errors += 1
                
                if consecutive_errors >= max_consecutive_errors:
                    self.logger.error(f"Reached {max_consecutive_errors} consecutive errors. Reinitializing driver...")
                    self.driver.quit()
                    self.driver = self._init_driver()
                    consecutive_errors = 0
                
                self._human_delay(300, 350)
            
            finally:
                self.logger.info("Iteration complete.")

if __name__ == '__main__':
    # Можно настроить параметры при запуске
    parser = AutoruParser(max_screenshots=10, max_screenshot_dirs=5)
    parser.parse()
