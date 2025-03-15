import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
os.environ.update({'DJANGO_ALLOW_ASYNC_UNSAFE': "true"})

import django
django.setup()

import asyncio
import json
import redis.asyncio as redis
from aiogram import Bot
from asgiref.sync import sync_to_async
from django.db import close_old_connections

from users.models import UserFilters, User  # Импортируй свою модель
from utils import check_filters  # Функция для проверки фильтров
from config import REDIS_HOST, REDIS_PORT


import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot_logs.log', mode='a')  # Запись логов в файл 'bot_logs.log'
    ]
)

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
bot = Bot(token=TOKEN)


async def get_all_ads(redis_client: redis.Redis):
    """Получает все объявления из Redis."""
    ad_keys = await redis_client.keys("*")  # Получаем все ключи
    ads = {}

    for ad_id in ad_keys:
        key_type = await redis_client.type(ad_id)
        if key_type != "string":
            continue  # Пропускаем нестроковые ключи
        ad_data = await redis_client.get(ad_id)  # Получаем JSON объявления
        if ad_data:
            try:
                ads[ad_id] = ad_data  # Сохраняем объявление как есть, не парсим в json пока
            except json.JSONDecodeError:
                print(f"Ошибка декодирования JSON для объявления {ad_id}")
    
    return ads


async def send_ads_by_filters(redis_client: redis.Redis):
    """Отправляет объявления пользователям по их фильтрам."""
    
    # Получаем все новые объявления из Redis
    ads = await get_all_ads(redis_client)
    logging.info(f"Найдено {len(ads)} объявлений")
    if not ads:
        return

    # Получаем всех пользователей с фильтрами
    users_monitoring_enabled = await sync_to_async(list)(User.objects.filter(monitoring_enabled=True))
    
    users = await sync_to_async(list)(UserFilters.objects.all())

    # Получаем набор проверенных объявлений
    checked_ads = await redis_client.smembers("ads:checked")  # Получаем все обработанные объявления

    for ad_id, ad_data in ads.items():
        if ad_id in checked_ads:
            continue  # Пропускаем уже обработанное объявление

        ad = json.loads(ad_data)  # Парсим данные объявления в json

        for user in users:
            if user.user_id in [u.user_id for u in users_monitoring_enabled]:
                filters = {
                    "platform": user.platform,
                    "price": user.price,
                    "brand": user.brand,
                    "engine": user.engine,
                    "mileage": user.mileage,
                    "gearbox": user.gearbox,
                    "owners": user.owners,
                    "condition": user.condition,
                    "seller": user.seller,
                    "city": user.city,
                    "year": user.year,
                    "body_type": user.body_type,
                    "color": user.color,
                    "drive": user.drive,
                    "steering": user.steering,
                    "ad_type": user.ad_type,
                }

                if check_filters(ad, filters):
                    await send_ad_to_user(user.user_id, ad)
                    logging.info(f"Отправлено объявление {ad_id} пользователю {user.user_id}")

        # После обработки добавляем объявление в "проверенные"
        await redis_client.sadd("ads:checked", ad_id)


async def send_ad_to_user(user_id, ad):
    """Отправляет объявление пользователю."""
    text = (
        f" [{ad['name'].title()} ({ad['year']})]({ad['link']})\n\n"
        f"💰 *Цена:* {ad['price']} ₽\n"
        f"📍 *Город:* {ad['city'].title()}\n"
        f"🚗 *Марка:* {ad['brand'].title()}\n"
        f"🚗 *Модель:* {ad['model'].title()}\n"
        f"📅 *Год:* {ad['year']}\n"
        f"📱 *Платформа:* {ad['platform']}\n\n"
        
        f"🔧 *Параметры:*\n"
        f"⛽ _Двигатель: {ad['engine']}_\n"
        f"📏 _Пробег: {ad['mileage']} км_\n"
        f"⚙️ _Коробка: {ad['gearbox']}_\n"
        f"🔧 _Привод: {ad['drive']}_\n"
        f"🚗 _Руль: {ad['steering']}_\n"
        f"🏷 _Тип кузова: {ad['body_type']}_\n"
        f"🎨 _Цвет: {ad['color']}_\n"
        f"👤 _Владельцев: {ad['owners']}_\n"
        f"🏷 _Состояние: {ad['condition']}_\n\n"
        
        f"🏢 *Продавец:* {ad['seller']}\n"
        f"📜 *Тип объявления:* {ad['ad_type']}\n"
        # f"🔗 *Ссылка:* {ad['link'].replace('_', r'\_')}"
    )

    try:
        await bot.send_photo(chat_id=user_id, photo=ad["image"], caption=text, parse_mode="Markdown")
    except Exception as e:
        print(f"❌ Ошибка photo пользователю {user_id}: {e}, объявление: {ad}")
        await bot.send_message(chat_id=user_id, text=text, parse_mode="Markdown")

async def main():
    redis_client = await redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

    while True:
        await send_ads_by_filters(redis_client)
        logging.info("Проверка фильтров завершена, ждем 30 секунд...")
        await asyncio.sleep(30)  # Проверять каждые 30 секунд
        close_old_connections()  # Закрываем старые соединения с БД

if __name__ == "__main__":
    asyncio.run(main())
    logging.info("Ads sender is running...")
