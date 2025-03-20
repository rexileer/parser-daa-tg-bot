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
    "Тип объявлений": ["б/у", "новый"],
}
     
def filter_keyboard(filter_name: str, selected_values=None) -> InlineKeyboardMarkup:
    if selected_values is None:
        selected_values = []
    inline_keyboard = []
    options = FILTER_MAPPING_KB.get(filter_name)
    if options:
        for option in options:
            # Если значение выбрано, добавляем галочку, иначе – крестик (или другой символ)
            if option in selected_values:
                text = f"✅ {option}"
            else:
                text = f"{option}"
            inline_keyboard.append([InlineKeyboardButton(
                text=text,
                callback_data=f"toggle_filter_{filter_name}_{option}"
            )])
        # Кнопка "Назад" для завершения выбора
        inline_keyboard.append([InlineKeyboardButton(
            text="📜 Назад",
            callback_data="filters_edit",
        )])
        return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return None

def filter_keyboard_back_button() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
        text="📜 Назад",
        callback_data="filters_edit",
    )]])