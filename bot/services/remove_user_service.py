from django.db import transaction
from users.models import User, UserFilters

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot_logs.log', mode='a')  # Запись логов в файл 'bot_logs.log'
    ]
)

logger = logging.getLogger(__name__)


async def remove_user_from_db(user_id: int):
    """
    Удаляет пользователя и связанные с ним фильтры из базы данных.
    """
    try:
        async with transaction.atomic():
            # Удаляем фильтры пользователя
            await UserFilters.objects.filter(user_id=user_id).adelete()
            
            # Удаляем самого пользователя
            deleted, _ = await User.objects.filter(id=user_id).adelete()
            
            if deleted:
                logger.info(f"Пользователь {user_id} успешно удален")
            else:
                logger.warning(f"Пользователь {user_id} не найден")
    except Exception as e:
        logger.error(f"Ошибка при удалении пользователя {user_id}: {e}")
