from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Включить мониторинг"),
            KeyboardButton(text="Выключить мониторинг"),
        ],
        [
            KeyboardButton(text="Фильтры"),
            KeyboardButton(text="Смотреть все объявления"),
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=False,
    input_field_placeholder="Выберите действие из меню",
    selective=True
)