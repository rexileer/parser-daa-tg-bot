from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


FILTER_MAPPING_KB = {
    "Площадка": ["avito", "drom", "autoru"],
    "Цена": None,
    "Марка": [
        "Lada (ВАЗ)",
        "Audi",
        "BMW",
        "Belgee",
        "Changan",
        "Chery",
        "Chevrolet",
        "Citroen",
        "Exeed",
        "Ford",
        "GAC",
        "Geely",
        "Haval",
        "Honda",
        "Hyundai",
        "Jaecoo",
        "Knewstar",
        "Land Rover",
        "Lexus",
        "LiXiang",
        "Mazda",
        "Mercedes-Benz",
        "Mitsubishi",
        "Nissan",
        "Omoda",
        "Opel",
        "Peugeot",
        "Porsche",
        "Renault",
        "Skoda",
        "Toyota",
        "Volkswagen",
        "Volvo"
    ],
    "Двигатель": [
        "бензин", 
        "дизель", 
        "гибрид", 
        "газ"
    ],
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
     
# Пагинация
PAGE_SIZE = 9  # Количество элементов на одной странице

def paginate_list(items, page_number):
    """Разбивает список на страницы по PAGE_SIZE элементов"""
    start_index = (page_number - 1) * PAGE_SIZE
    end_index = start_index + PAGE_SIZE
    return items[start_index:end_index]
     
     
def filter_keyboard(filter_name: str, selected_values=None, page=1) -> InlineKeyboardMarkup:
    if selected_values is None:
        selected_values = []
    inline_keyboard = []
    options = FILTER_MAPPING_KB.get(filter_name)
    if options:
        # Сначала определим, какие опции показывать на текущей странице
        options_per_page = 9  # 3x3
        start_index = (page - 1) * options_per_page
        end_index = start_index + options_per_page
        page_options = options[start_index:end_index]

        # Проходим по опциям и добавляем их в клавиатуру
        row = []  # Список для одной строки
        for idx, option in enumerate(page_options):
            # Если значение выбрано, добавляем галочку, иначе – крестик (или другой символ)
            if option in selected_values:
                text = f"✅ {option}"
            else:
                text = f"{option}"

            row.append(InlineKeyboardButton(
                text=text,
                callback_data=f"toggle_filter_{filter_name}_{option}_{page}"
            ))

            # Если достигли 3 кнопок в строке, добавляем строку в клавиатуру и очищаем row
            if len(row) == 3:
                inline_keyboard.append(row)
                row = []  # Сброс строки

        # Добавляем оставшиеся кнопки, если их меньше 3
        if row:
            inline_keyboard.append(row)
            
        # Кнопки для перехода между страницами
        page_buttons = []

        if page > 1:
            page_buttons.append(InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"filter_page_{filter_name}_{page - 1}"
            ))

        total_pages = (len(options) - 1) // PAGE_SIZE + 1
        page_buttons.append(InlineKeyboardButton(
            text=f"Страница {page} из {total_pages}",
            callback_data="none"
        ))

        if len(options) > page * options_per_page:
            page_buttons.append(InlineKeyboardButton(
                text="Вперёд ➡️",
                callback_data=f"filter_page_{filter_name}_{page+1}"
            ))

        if page_buttons:
            inline_keyboard.append(page_buttons)

        # Кнопка "Назад" для завершения выбора
        inline_keyboard.append([InlineKeyboardButton(
            text="⬅️ Вернуться к фильтрам",
            callback_data="filters_edit",
        )])
        return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return None

def filter_keyboard_back_button() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
        text="📜 Назад",
        callback_data="filters_edit",
    )]])