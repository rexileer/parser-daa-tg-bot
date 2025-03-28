from users.models import UserFilters
from django.contrib.postgres.fields import ArrayField
from django.db import models

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
        f"• *Тип объявлений:* _обычное, продвижение_ \n"
        f"• *Выбранный тип продавца:* _автодилер, частное лицо_ \n"
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
        f"• *Выбранный тип объявлений:* {filters.ad_type or 'Не указано'}\n"
        f"• *Выбранный тип продавца:* {filters.seller or 'Не указано'}\n"
    )

async def get_user_filters_from_db(user_id: int):
    filters, _ = await UserFilters.objects.aget_or_create(user_id=user_id)
    return filters

async def update_user_filter(user_id: int, field: str, value: str):
    """
    Обновляет значение фильтра для пользователя.
    
    Если поле является ArrayField:
      - Если value содержит запятую (", "), значит, это ручной ввод нескольких значений,
        и они преобразуются в список.
      - Если value не содержит запятую, происходит переключение выбранного значения:
        если значение уже присутствует в списке – оно удаляется, иначе – добавляется.
    
    Если поле является обычным CharField, значение сохраняется как строка.
    """
    filters, _ = await UserFilters.objects.aget_or_create(user_id=user_id)
    
    # Получаем объект поля по его имени
    model_field = UserFilters._meta.get_field(field)
    
    if isinstance(model_field, ArrayField):
        # Получаем текущее значение поля (список) или создаём пустой список
        current_values = getattr(filters, field) or []
        
        if ", " in value:
            # Ручной ввод нескольких значений, например: "val1, val2, val3"
            new_values = [v.strip() for v in value.split(",")]
        else:
            # Inline-обновление: переключаем значение
            if value in current_values:
                new_values = [v for v in current_values if v != value]
            else:
                new_values = current_values + [value]
        setattr(filters, field, new_values)
    else:
        # Для обычного текстового поля сохраняем значение напрямую
        setattr(filters, field, value)
    
    await filters.asave()
    
async def get_user_filter_values(user_id: int, field: str):
    filters = await get_user_filters_from_db(user_id)
    return getattr(filters, field) or []

async def clear_user_filter(user_id: int, field: str):
    filters, _ = await UserFilters.objects.aget_or_create(user_id=user_id)
    
    # Получаем информацию о поле из модели
    field_type = UserFilters._meta.get_field(field)
    
    # Очищаем в зависимости от типа поля
    if isinstance(field_type, ArrayField):
        setattr(filters, field, [])  # Для массивов — пустой список
    elif isinstance(field_type, (models.CharField, models.TextField)):
        setattr(filters, field, "")  # Для строк — пустая строка
    elif isinstance(field_type, (models.IntegerField, models.BigIntegerField, models.FloatField)):
        setattr(filters, field, None)  # Для чисел — None (или 0, если нужно)
    else:
        setattr(filters, field, None)  # Для остальных типов — None
    
    await filters.asave()