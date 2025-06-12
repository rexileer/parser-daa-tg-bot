from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from keyboards.inline.view_all_ads_kb import view_all_ads_keyboard
import os

import logging
logger = logging.getLogger(__name__)

router = Router()

@router.message(Command("all_ads"))
async def view_all_ads_command(message: Message):
    """
    Command to view all ads on the website
    """
    # Get the website URL from environment variable or use default
    website_url = os.getenv('WEBSITE_URL', 'http://localhost:8000')
    
    keyboard = view_all_ads_keyboard(website_url)
    
    await message.answer(
        "Нажмите на кнопку ниже, чтобы перейти на сайт со всеми объявлениями. "
        "На сайте вы можете настроить фильтры и найти интересующие вас объявления.",
        reply_markup=keyboard
    ) 