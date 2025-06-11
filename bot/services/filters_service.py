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
    
    # Функция для форматирования значений (может быть список или строка)
    def format_value(value):
        if isinstance(value, list):
            return ", ".join(value) if value else "Не указано"
        else:
            return value or "Не указано"
    
    return (
        f"⚙️ *Выбранные фильтры*\n\n"
        f"• *Выбранные площадки:* {format_value(filters.platform)}\n"
        f"• *Выбранный год выпуска:* {format_value(filters.year)}\n"
        f"• *Выбранная цена:* {format_value(filters.price)}\n"
        f"• *Выбранные города:* {format_value(filters.city)}\n"
        f"• *Выбранные марки:* {format_value(filters.brand)}\n"
        f"• *Выбранный диапазон пробега:* {format_value(filters.mileage)}\n"
        f"• *Выбранный тип двигателя:* {format_value(filters.engine)}\n"
        f"• *Выбранный цвет кузова:* {format_value(filters.color)}\n"
        f"• *Выбранный вид коробки передач:* {format_value(filters.gearbox)}\n"
        f"• *Выбранный привод:* {format_value(filters.drive)}\n"
        f"• *Выбранный руль:* {format_value(filters.steering)}\n"
        f"• *Выбранное кол-во владельцев:* {format_value(filters.owners)}\n"
        f"• *Выбранный тип кузова:* {format_value(filters.body_type)}\n"
        f"• *Выбранное состояние:* {format_value(filters.condition)}\n"
        f"• *Выбранный тип объявлений:* {format_value(filters.ad_type)}\n"
        f"• *Выбранный тип продавца:* {format_value(filters.seller)}\n"
    )

async def get_user_filters_from_db(user_id: int):
    filters, _ = await UserFilters.objects.aget_or_create(user_id=user_id)
    return filters

async def update_user_filter(user_id: int, field: str, value):
    """
    Обновляет значение фильтра для пользователя.
    
    Параметр value может быть:
    - Строкой: обычное значение или строка с разделителями для массива
    - Списком: прямая установка массива значений
    - None: очистка значения
    """
    filters, _ = await UserFilters.objects.aget_or_create(user_id=user_id)
    
    # Получаем объект поля по его имени
    model_field = UserFilters._meta.get_field(field)
    
    # Если значение уже является списком, используем его как есть
    if isinstance(value, list):
        setattr(filters, field, value)
    # Если это ArrayField и значение - строка с разделителями
    elif isinstance(model_field, ArrayField) and isinstance(value, str) and "," in value:
        new_values = [v.strip() for v in value.split(",")]
        setattr(filters, field, new_values)
    # Обычное текстовое поле или одно значение для ArrayField
    else:
        setattr(filters, field, value)
    
    await filters.asave()
    
async def get_user_filter_values(user_id: int, field: str):
    filters = await get_user_filters_from_db(user_id)
    value = getattr(filters, field)
    
    # Если значение не пустое и не список, преобразуем его в список с одним элементом
    if value and not isinstance(value, list):
        return [value]
    
    return value or []

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