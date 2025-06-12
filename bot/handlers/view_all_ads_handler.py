from aiogram import Router, F
from aiogram.types import Message
from keyboards.inline.view_all_ads_kb import view_all_ads_keyboard
import os

import logging
logger = logging.getLogger(__name__)

router = Router()

@router.message(F.text == "Смотреть все объявления")
async def view_all_ads_handler(message: Message):
    """
    Handler for the "Смотреть все объявления" button
    """
    # Get the website URL from environment variable or use default
    website_url = os.getenv('WEBSITE_URL', 'https://example.com')
    
    # Check if the URL is valid for Telegram (must be https:// and not localhost)
    if website_url.startswith('http://') or 'localhost' in website_url or '127.0.0.1' in website_url:
        await message.delete()
        await message.answer(
            "⚠️ Для просмотра объявлений на сайте перейдите по адресу, указанному в настройках.\n\n"
            "Примечание: В данный момент сайт доступен только по IP-адресу или домену, а не через localhost."
        )
    else:
        keyboard = view_all_ads_keyboard(website_url)
        
        await message.delete()
        await message.answer(
            "Нажмите на кнопку ниже, чтобы перейти на сайт со всеми объявлениями. "
            "На сайте вы можете настроить фильтры и найти интересующие вас объявления.",
            reply_markup=keyboard
        ) 