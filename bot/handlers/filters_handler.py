from aiogram import Router, F
from aiogram.types import Message


import logging
logger = logging.getLogger(__name__)

router = Router()


@router.message(F.text == "Фильтры")
async def enable_filter_callback(message: Message):
    user_id = message.from_user.id
    await message.answer(f"Фильтры для {user_id}")

