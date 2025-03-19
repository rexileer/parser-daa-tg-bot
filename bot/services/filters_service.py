from users.models import UserFilters

async def get_user_filters_explain() -> str:
    """ Получает фильтры пользователя из БД и форматирует их для вывода """

    return (
        f"⚙️ *Описание фильтров*\n\n"
        f"• *Выбранные площадки:* _drom, autoru, avito_ \n"
        f"• *Выбранный год выпуска:* _1900-2025_ \n"
        f"• *Выбранная цена:* _0-99999999_ \n"
        f"• *Выбранные города:* _название города_ \n"
        f"• *Выбранные марки:* _название бренда_ \n"
        f"• *Выбранный диапазон пробега:* _0-99999999_ \n"
        f"• *Выбранный тип двигателя:* _дизель, бензин, газ, гибрид_ \n"
        f"• *Выбранный цвет кузова:* _цвет_ \n"
        f"• *Выбранный вид коробки передач:* _робот, механика, вариатор, автомат_ \n"
        f"• *Выбранный привод:* _передний, задний, полный_ \n"
        f"• *Выбранный руль:* _левый, правый_ \n"
        f"• *Выбранное кол-во владельцев:* _0-99_ \n"
        f"• *Выбранный тип кузова:* _тип кузова_ \n"
        f"• *Выбранное состояние:* _битый, не битый_ \n"
        f"• *Тип объявлений:* _новый, второй рынок_ \n"
        f"• *Выбранный тип продавца:* _компания, частное лицо_ \n"
    )

async def get_user_filters(user_id: int) -> str:
    """ Получает фильтры пользователя из БД и форматирует их для вывода """
    filters = await get_user_filters_from_db(user_id)
    
    if not filters:
        return "⚠️ Фильтры не заданы"
    
    return (
        f"⚙️ *Выбранные фильтры*\n\n"
        f"• *Выбранные площадки:* {filters.platform or 'Не указано'}\n"
        f"• *Выбранный год выпуска:* {filters.year or 'Не указано'}\n"
        f"• *Выбранная цена:* {filters.price or 'Не указано'}\n"
        f"• *Выбранные города:* {filters.city or 'Не указано'}\n"
        f"• *Выбранные марки:* {filters.brand or 'Не указано'}\n"
        f"• *Выбранный диапазон пробега:* {filters.mileage or 'Не указано'}\n"
        f"• *Выбранный тип двигателя:* {filters.engine or 'Не указано'}\n"
        f"• *Выбранный цвет кузова:* {filters.color or 'Не указано'}\n"
        f"• *Выбранный вид коробки передач:* {filters.gearbox or 'Не указано'}\n"
        f"• *Выбранный привод:* {filters.drive or 'Не указано'}\n"
        f"• *Выбранный руль:* {filters.steering or 'Не указано'}\n"
        f"• *Выбранное кол-во владельцев:* {filters.owners or 'Не указано'}\n"
        f"• *Выбранный тип кузова:* {filters.body_type or 'Не указано'}\n"
        f"• *Выбранное состояние:* {filters.condition or 'Не указано'}\n"
        f"• *Тип объявлений:* {filters.ad_type or 'Не указано'}\n"
        f"• *Выбранный тип продавца:* {filters.seller or 'Не указано'}\n"
    )

async def get_user_filters_from_db(user_id: int):
    filters, _ = await UserFilters.objects.aget_or_create(user_id=user_id)
    return filters

async def update_user_filter(user_id: int, field: str, value: str):
    filters, _ = await UserFilters.objects.aget_or_create(user_id=user_id)
    setattr(filters, field, value)  # Динамическое обновление поля
    await filters.asave()
