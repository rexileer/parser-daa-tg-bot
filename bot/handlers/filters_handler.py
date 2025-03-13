from aiogram.types import Message
from aiogram import Router, F
from keyboards.inline.filters_kb import filters_keyboard
from services.filters_service import get_user_filters_explain


router = Router()

@router.message(F.text == "Фильтры")
async def enable_filter_callback(message: Message):
    filters_text = await get_user_filters_explain()
    
    keyboard = filters_keyboard()
    await message.answer(filters_text, reply_markup=keyboard, parse_mode="Markdown")
