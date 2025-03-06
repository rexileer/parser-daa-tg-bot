from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Включить мониторинг"),
            KeyboardButton(text="Выключить мониторинг"),
        ],
        [
            KeyboardButton(text="Фильтры"),
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Choose action from menu",
    selective=True
)