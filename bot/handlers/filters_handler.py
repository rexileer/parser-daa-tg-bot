from aiogram.types import Message
from aiogram import Router, F
from asgiref.sync import sync_to_async
from users.models import UserFilters
from keyboards.inline.filters_kb import filters_keyboard

router = Router()

async def get_user_filters(user_id: int) -> str:
    """ Получает фильтры пользователя из БД и форматирует их для вывода """
    filters = await sync_to_async(UserFilters.objects.filter(user_id=user_id).first)()
    
    if not filters:
        return "⚠️ Фильтры не заданы"
    
    return (
        f"⚙️ *Настройка фильтра*\n\n"
        f"• *Выбранная цена:* {filters.price or 'Не указано'}\n"
        f"• *Выбранные платформы:* {filters.platform or 'Не указано'}\n"
        f"• *Выбранные города:* {filters.city or 'Не указано'}\n"
        f"• *Выбранные марки:* {filters.brand or 'Не указано'}\n"
        f"• *Выбранный год выпуска:* {filters.year or 'Не указано'}\n"
        f"• *Выбранное кол-во владельцев:* {filters.owners or 'Не указано'}\n"
        f"• *Выбранный диапазон пробега:* {filters.mileage or 'Не указано'}\n"
        f"• *Выбранный тип двигателя:* {filters.engine or 'Не указано'}\n"
        f"• *Выбранный тип кузова:* {filters.body_type or 'Не указано'}\n"
        f"• *Выбранный цвет кузова:* {filters.color or 'Не указано'}\n"
        f"• *Выбранное состояние:* {filters.condition or 'Не указано'}\n"
        f"• *Выбранный тип продавца:* {filters.seller or 'Не указано'}\n"
        f"• *Выбранный привод:* {filters.drive or 'Не указано'}\n"
        f"• *Выбранный руль:* {filters.steering or 'Не указано'}\n"
        f"• *Выбранный вид коробки передач:* {filters.gearbox or 'Не указано'}\n"
        f"• *Тип объявлений:* {filters.ad_type or 'Не указано'}"
    )

@router.message(F.text == "Фильтры")
async def enable_filter_callback(message: Message):
    user_id = message.from_user.id
    filters_text = await get_user_filters(user_id)
    
    keyboard = filters_keyboard()  # Функция, создающая кнопки выбора фильтров
    await message.answer(filters_text, reply_markup=keyboard, parse_mode="Markdown")
