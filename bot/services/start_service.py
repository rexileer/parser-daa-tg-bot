from asgiref.sync import sync_to_async
from editing.models import StartCommandResponse


async def get_start_message():
    msg = await StartCommandResponse.objects.afirst()
    return msg.text if msg else "Привет! Добро пожаловать в бота."
