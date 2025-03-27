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
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter
from asgiref.sync import sync_to_async
from django.db import close_old_connections

from users.models import UserFilters, User  # Импортируй свою модель
from utils import check_filters  # Функция для проверки фильтров
from config import REDIS_HOST, REDIS_PORT
from services.remove_user_service import remove_user_from_db

import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot_logs.log', mode='a')
    ]
)

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
bot = Bot(token=TOKEN)


async def get_all_ads(redis_client: redis.Redis):
    """Получает все объявления из Redis."""
    ad_keys = await redis_client.keys("*")
    ads = {}
    for ad_id in ad_keys:
        key_type = await redis_client.type(ad_id)
        if key_type != "string":
            continue  # Пропускаем нестроковые ключи
        ad_data = await redis_client.get(ad_id)
        if ad_data:
            try:
                ads[ad_id] = ad_data  # Сохраняем данные как есть
            except json.JSONDecodeError:
                logging.error(f"Ошибка декодирования JSON для объявления {ad_id}")
    return ads


async def send_ads_by_filters(redis_client: redis.Redis):
    """Отправляет объявления пользователям по их фильтрам."""
    ads = await get_all_ads(redis_client)
    logging.info(f"Найдено {len(ads)} объявлений")
    if not ads:
        return

    users_monitoring_enabled = await sync_to_async(list)(User.objects.filter(monitoring_enabled=True))
    users = await sync_to_async(list)(UserFilters.objects.all())
    checked_ads = await redis_client.smembers("ads:checked")

    for ad_id, ad_data in ads.items():
        if ad_id in checked_ads:
            continue  # Пропускаем уже обработанное объявление

        ad = json.loads(ad_data)
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


import logging

# Вспомогательные функции для экранирования и оформления MarkdownV2
def escape_md_v2(text: str) -> str:
    """
    Экранирует все спецсимволы, требуемые MarkdownV2.
    Список символов: _ * [ ] ( ) ~ ` > # + - = | { } . !
    """
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for ch in special_chars:
        text = text.replace(ch, f"\\{ch}")
    return text

def bold_md(text: str) -> str:
    """Оформляет текст как жирный (MarkdownV2)."""
    return f"*{text}*"

def italic_md(text: str) -> str:
    """Оформляет текст как курсив (MarkdownV2)."""
    return f"_{text}_"

def link_md(title: str, url: str) -> str:
    """Оформляет ссылку (MarkdownV2)."""
    return f"[{title}]({url})"

async def send_ad_to_user(user_id, ad):
    """
    Отправляет объявление пользователю. Динамические данные проходят экранирование,
    затем форматируются с помощью функций bold_md, italic_md и link_md.
    """
    # Экранируем и форматируем все динамические поля
    name = escape_md_v2(ad.get('name', '').title())
    year = escape_md_v2(str(ad.get('year', '')))
    ad_link = escape_md_v2(ad.get('link', ''))
    price = escape_md_v2(str(ad.get('price', '')))
    city = escape_md_v2(ad.get('city', '').title())
    brand = escape_md_v2(ad.get('brand', '').title())
    model = escape_md_v2(ad.get('model', '').title())
    engine = escape_md_v2(ad.get('engine', ''))
    mileage = escape_md_v2(str(ad.get('mileage', '')))
    gearbox = escape_md_v2(ad.get('gearbox', ''))
    drive = escape_md_v2(ad.get('drive', ''))
    steering = escape_md_v2(ad.get('steering', ''))
    body_type = escape_md_v2(ad.get('body_type', ''))
    color = escape_md_v2(ad.get('color', ''))
    owners = escape_md_v2(str(ad.get('owners', '')))
    condition = escape_md_v2(ad.get('condition', ''))
    seller = escape_md_v2(ad.get('seller', ''))
    ad_type = escape_md_v2(ad.get('ad_type', ''))
    platform = escape_md_v2(ad.get('platform', ''))

    # Формируем текстовое сообщение с применением MarkdownV2
    text_msg = (
        f"{bold_md(name)}\n\n"
        f"{bold_md('💰 Цена:')} {price} ₽\n"
        f"{bold_md('📍 Город:')} {city}\n"
        f"{bold_md('🚗 Марка:')} {brand}\n"
        f"{bold_md('🚗 Модель:')} {model}\n"
        f"{bold_md('📅 Год:')} {year}\n"
        f"{bold_md('📱 Площадка:')} {platform}\n\n"
        f"{bold_md('🔧 Параметры:')}\n"
        f"{italic_md('⛽ Двигатель:')} {engine}\n"
        f"{italic_md('📏 Пробег:')} {mileage} км\n"
        f"{italic_md('⚙️ Коробка:')} {gearbox}\n"
        f"{italic_md('🔧 Привод:')} {drive}\n"
        f"{italic_md('🚗 Руль:')} {steering}\n"
        f"{italic_md('🏷 Тип кузова:')} {body_type}\n"
        f"{italic_md('🎨 Цвет:')} {color}\n"
        f"{italic_md('👤 Владельцев:')} {owners}\n"
        f"{italic_md('🏷 Состояние:')} {condition}\n\n"
        f"{bold_md('🏢 Продавец:')} {seller}\n"
        f"{bold_md('📜 Тип объявления:')} {ad_type}\n\n"
        f"{link_md('Ссылка на объявление', ad_link)}\n"
    )

    try:
        await bot.send_photo(chat_id=user_id, photo=ad["image"], caption=text_msg, parse_mode="MarkdownV2")
        asyncio.sleep(0.5)
    except TelegramForbiddenError:
        logging.info(f"Пользователь {user_id} заблокировал бота. Удаляем его из базы.")
        await remove_user_from_db(user_id)  # Удалить или пометить пользователя
    except TelegramRetryAfter as e:
        logging.error(f"⏳ Превышен лимит запросов к Telegram API: ожидание {e.retry_after} сек.")
        await asyncio.sleep(e.retry_after)
    except Exception as e:
        logging.error(f"❌ Ошибка отправки пользователю {user_id}: {e}, объявление: {ad}")
        await bot.send_message(chat_id=user_id, text=text_msg, parse_mode="MarkdownV2")



async def main():
    redis_client = await redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    while True:
        await send_ads_by_filters(redis_client)
        logging.info("Проверка фильтров завершена, ждем 30 секунд...")
        await asyncio.sleep(30)
        close_old_connections()

if __name__ == "__main__":
    asyncio.run(main())
    logging.info("Ads sender is running...")
