from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Функция для создания клавиатуры с фильтрами
def filters_keyboard():
    # Строки с фильтрами
    filters = [
        ['Площадка', 'Цена', 'Марка'],
        ['Двигатель', 'Пробег', 'Коробка'],
        ['Кол-во владельцев', 'Состояние', 'Продавец'],
        ['Город', 'Год выпуска', 'Тип кузова'],
        ['Цвет кузова', 'Привод', 'Руль'],
        ['Тип объявлений']
    ]
    
    # Формируем inline клавиатуру
    inline_keyboard = []
    
    # Добавление кнопок на клавиатуру
    for filter_row in filters:
        buttons = [InlineKeyboardButton(text=filter_name, callback_data=filter_name) for filter_name in filter_row]
        inline_keyboard.append(buttons)
    
    # Создание и возврат клавиатуры
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    
    return keyboard
