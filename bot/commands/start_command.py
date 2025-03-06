from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from services.start_service import get_start_message

import logging
logger = logging.getLogger(__name__)

router = Router()

@router.message(CommandStart())
async def start(message: Message):
    logger.info(f"Received /start command from {message.from_user.id}")  
    text = await get_start_message()
    await message.answer(text, reply_markup=None)
    logger.info(f"Sent start message to {message.from_user.id}")