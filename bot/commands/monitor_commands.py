from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from services.monitoring_switch_service import enable_monitoring, disable_monitoring

import logging
logger = logging.getLogger(__name__)

router = Router()

@router.message(Command("monitor_on"))
async def start_monitoring_command(message: Message):
    user_id = message.from_user.id
    await enable_monitoring(user_id=user_id)
    logger.info(f"Monitoring is enabled for user {user_id}")
    await message.answer("✅ Мониторинг включен")


@router.message(Command("monitor_off"))
async def stop_monitoring_command(message: Message):
    user_id = message.from_user.id
    await disable_monitoring(user_id=user_id)
    logger.info(f"Monitoring is disabled for user {user_id}")
    await message.answer("❌ Мониторинг выключен") 