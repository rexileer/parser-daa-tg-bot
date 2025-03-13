from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def check_filters_keyboard():
    inline_keyboard = []
    
    buttons = [
        InlineKeyboardButton(text="✅Запустить", callback_data="start_filtering"),
        InlineKeyboardButton(text="Редактировать", callback_data="filters_edit"), 
    ]
    inline_keyboard.append(buttons)
    
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
