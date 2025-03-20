from aiogram import Router, F
from aiogram.types import Message

from services.monitoring_switch_service import enable_monitoring, disable_monitoring

import logging
logger = logging.getLogger(__name__)

router = Router()

@router.message(F.text == "Включить мониторинг")
async def start_monitoring_handler(message: Message):
    user_id = message.from_user.id
    await enable_monitoring(user_id=user_id)
    logger.info(f"Monitoring is enabled for user {user_id}")
    await message.delete()
    await message.answer("Мониторинг включен")


@router.message(F.text == "Выключить мониторинг")
async def stop_monitoring_handler(message: Message):
    user_id = message.from_user.id
    await disable_monitoring(user_id=user_id)
    logger.info(f"Monitoring is disabled for user {user_id}")
    await message.delete()
    await message.answer("Мониторинг выключен")
