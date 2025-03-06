from users.models import User

async def enable_monitoring(user_id: int):
    user, _ = await User.objects.aget_or_create(user_id=user_id)
    if user:
        user.monitoring_enabled = True
        await user.asave()
    
async def disable_monitoring(user_id: int):
    user, _ = await User.objects.aget_or_create(user_id=user_id)
    if user:
        user.monitoring_enabled = False
        await user.asave()
