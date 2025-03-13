import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
os.environ.update({'DJANGO_ALLOW_ASYNC_UNSAFE': "true"})

import django
django.setup()

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties

from dotenv import load_dotenv

from commands import start_command
from handlers import monitoring_handler, filters_handler
from callbacks import filters_callback, filters_check_callback
from ads_sender import main as start_ads_sender

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot_logs.log', mode='a')  # Запись логов в файл 'bot_logs.log'
    ]
)

logger = logging.getLogger(__name__)


load_dotenv(encoding='utf-8')

async def main():
    bot = Bot(os.getenv('TELEGRAM_BOT_TOKEN'), default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher()
    
    dp.include_routers(
        start_command.router,
        monitoring_handler.router,
        filters_handler.router,
        filters_callback.router,
        filters_check_callback.router,
    )
    
    await asyncio.gather(
        bot.delete_webhook(drop_pending_updates=True),
        dp.start_polling(bot),
        start_ads_sender(),
    )

if __name__ == "__main__":
    asyncio.run(main())