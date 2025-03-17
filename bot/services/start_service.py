from editing.models import StartCommandResponse
# from users.models import User

async def get_start_message():
    msg = await StartCommandResponse.objects.afirst()
    return msg.text if msg else "Привет! Добро пожаловать в бота."
