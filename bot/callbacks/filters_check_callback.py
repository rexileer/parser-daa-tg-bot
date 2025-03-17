from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards.inline.filters_kb import filters_keyboard
from services.filters_service import get_user_filters_explain
from services.monitoring_switch_service import enable_monitoring

import logging
logger = logging.getLogger(__name__)

router = Router()

@router.callback_query(F.data == "filters_edit")
async def edit_filter_callback(callback: CallbackQuery):
    filters_text = await get_user_filters_explain()
    
    keyboard = filters_keyboard()
    await callback.message.edit_text(filters_text, reply_markup=keyboard, parse_mode="Markdown")
    
@router.callback_query(F.data == "start_filtering")
async def start_filtering_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    await enable_monitoring(user_id=user_id)
    logger.info(f"Monitoring is enabled for user {user_id}")
    filters_text = "Мониторинг запущен!"

    await callback.message.edit_text(filters_text)