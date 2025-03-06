from aiogram import Router, F
from aiogram.types import Message

from keyboards.inline.filters_kb import filters_keyboard

import logging
logger = logging.getLogger(__name__)

router = Router()


@router.message(F.text == "Фильтры")
async def enable_filter_callback(message: Message):
    user_id = message.from_user.id
    keyboard = filters_keyboard()
    await message.answer(f"Фильтры для {user_id}", reply_markup=keyboard)

