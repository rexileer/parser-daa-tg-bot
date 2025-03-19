from editing.models import BroadcastMessage
from users.models import User
from asgiref.sync import sync_to_async
from django.utils.timezone import now


@sync_to_async
def get_broadcast_messages():
    """Получение сообщений для рассылки из базы данных"""
    return BroadcastMessage.objects.filter(is_sent=False, send_time__lte=now())

@sync_to_async
def get_users():
    """Получение всех пользователей из базы данных"""
    return User.objects.all()