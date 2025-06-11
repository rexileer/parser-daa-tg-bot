from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from keyboards.inline.filters_kb import filters_keyboard
from services.filters_service import get_user_filters_explain

import logging
logger = logging.getLogger(__name__)

router = Router()

@router.message(Command("filters"))
async def filters_command(message: Message):
    filters_text = await get_user_filters_explain()
    keyboard = filters_keyboard()
    await message.answer(filters_text, reply_markup=keyboard, parse_mode="Markdown") 