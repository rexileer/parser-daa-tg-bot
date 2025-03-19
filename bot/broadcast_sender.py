import asyncio
import logging
import os
from dotenv import load_dotenv
from django.db import close_old_connections
from aiogram.types import FSInputFile
from io import BytesIO
from services.broadcast_service import get_broadcast_messages, get_users

load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Функция для отправки сообщений
async def send_message(bot, user_id, text=None, image=None, video=None):
    """Отправка сообщений пользователям"""
    try:
        if video:
            video_input = FSInputFile(video.path)
            await bot.send_video(user_id, video_input, caption=text)
        elif image:
            image_input = FSInputFile(image.path)
            await bot.send_photo(user_id, image_input, caption=text)
        elif text:
            await bot.send_message(user_id, text)
        else:
            logging.warning(f"Пустая рассылка")

        logging.info(f"Сообщение отправлено {user_id}")
    except Exception as e:
        logging.error(f"Ошибка отправки {user_id}: {e}")


# Функция рассылки сообщений


async def broadcast(bot):
    """Функция рассылки сообщений"""
    logging.info("Начало проверки рассылок...")

    try:
        close_old_connections()  # Закрываем старые соединения с БД
        messages = await get_broadcast_messages()

        if not messages.exists():
            logging.info("Нет новых сообщений для отправки")
            return

        for message in messages:
            users = await get_users()
            for user in users:
                await send_message(bot, user.user_id, message.text, message.image, message.video)

            # Помечаем сообщения как отправленные
            message.is_sent = True
            message.save()

        logging.info("Рассылка завершена.")
    except Exception as e:
        logging.error(f"Ошибка в broadcast(): {e}")

async def broadcast_loop(bot):
    """Цикл, который периодически запускает broadcast()"""
    while True:
        await broadcast(bot)
        logging.info("Пауза перед следующей проверкой (30 сек)")
        await asyncio.sleep(30)


