from users.models import UserFilters

async def get_user_filters(user_id: int):
    filters, _ = await UserFilters.objects.aget_or_create(user_id=user_id)
    return filters

async def update_user_filter(user_id: int, field: str, value: str):
    filters, _ = await UserFilters.objects.aget_or_create(user_id=user_id)
    setattr(filters, field, value)  # Динамическое обновление поля
    await filters.asave()

FILTER_MAPPING = {
    "Площадка": "platform",
    "Цена": "price",
    "Марка": "brand",
    "Двигатель": "engine",
    "Пробег": "mileage",
    "Коробка": "gearbox",
    "Кол-во владельцев": "owners",
    "Состояние": "condition",
    "Продавец": "seller",
    "Город": "city",
    "Год выпуска": "year",
    "Тип кузова": "body_type",
    "Цвет кузова": "color",
    "Привод": "drive",
    "Руль": "steering",
    "Тип объявлений": "ad_type",
}
