from editing.models import StartCommandResponse
# from users.models import User

async def get_start_message():
    msg = await StartCommandResponse.objects.afirst()
    return msg.text if msg else "Привет! Добро пожаловать в бота."

# async def check_user_in_db(user_id: int):
#     if await User.objects.aget(user_id=user_id):
#         return True
#     return False