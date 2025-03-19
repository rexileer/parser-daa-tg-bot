from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


FILTER_MAPPING_KB = {
    "Площадка": ["avito", "drom", "autoru"],
    "Цена": None,
    "Марка": None,
    "Двигатель": ["бензин", "дизель", "гибрид", "газ"],
    "Пробег": None,
    "Коробка": ["автомат", "механика", "робот", "вариатор"],
    "Кол-во владельцев": None,
    "Состояние": ["не битый", "битый"],
    "Продавец": ["частное лицо", "компания"],
    "Город": None,
    "Год выпуска": None,
    "Тип кузова": None,
    "Цвет кузова": None,
    "Привод": ["полный", "передний", "задний"],
    "Руль": ["левый", "правый"],
    "Тип объявлений": ["второй рынок", "новый"],
}

def filter_keyboard(filter_name: str) -> InlineKeyboardMarkup:
    inline_keyboard = []

    if filter_name in FILTER_MAPPING_KB and FILTER_MAPPING_KB[filter_name] != None:
        for filter_value in FILTER_MAPPING_KB[filter_name]:
            inline_keyboard.append([InlineKeyboardButton(text=filter_value, callback_data=f"value_filter_{filter_name}_{filter_value}")])
        return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
        
    return None
