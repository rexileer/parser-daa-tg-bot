from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import State, StatesGroup

from services.filters_service import update_user_filter, get_user_filters, get_user_filter_values, clear_user_filter, get_user_filters_explain
from keyboards.inline.check_filters_kb import check_filters_keyboard
from keyboards.inline.filters_mapping_kb import filter_keyboard, filter_keyboard_back_button
from keyboards.inline.filters_kb import filters_keyboard
from .filter_mapping import FILTER_MAPPING_LANGUAGE, FILTER_MAPPING_DESCRIPTION


class FilterStates(StatesGroup):
    entering_value = State()

router = Router()

@router.callback_query(F.data.startswith("filter_"))
async def filter_handler(callback: CallbackQuery, state: FSMContext):
    # Проверяем, если callback_data содержит пагинацию
    if callback.data.startswith("filter_page_"):
        # Разбираем callback_data: например, page_Марка_2
        parts = callback.data.split("_")
        filter_name_rus = parts[2]
        filter_name = FILTER_MAPPING_LANGUAGE.get(filter_name_rus)  # Перевод в поле модели
        filter_description = FILTER_MAPPING_DESCRIPTION.get(filter_name_rus)
        page = int(parts[3])
        current_values = await get_user_filter_values(callback.from_user.id, filter_name)

        # Обновляем клавиатуру с учетом выбранной страницы
        keyboard = filter_keyboard(filter_name_rus, current_values, page)

        # Обновляем сообщение с новой клавиатурой
        await callback.message.edit_text(
            f"Выберите {filter_name_rus}\n"
            f"Формат: «{filter_description}»",
            reply_markup=keyboard if keyboard else filter_keyboard_back_button(filter_name=filter_name_rus),
        )
        return
    filter_name_rus = callback.data.replace("filter_", "")  # Русское название
    filter_name = FILTER_MAPPING_LANGUAGE.get(filter_name_rus)  # Перевод в поле модели
    filter_description = FILTER_MAPPING_DESCRIPTION.get(filter_name_rus)
    
    if not filter_name:
        await callback.message.answer("❌ Ошибка: фильтр не найден.")
        return
    
    current_values = await get_user_filter_values(callback.from_user.id, filter_name)
    
    
    keyboard = filter_keyboard(filter_name_rus, current_values, page=1)
    
    sent_message = await callback.message.edit_text(
        f"Введите значение для {filter_name_rus}\n"
        f"Формат: «{filter_description}»",
        reply_markup=keyboard if keyboard else filter_keyboard_back_button(filter_name=filter_name_rus),
    )

    if not keyboard:
        await state.update_data(sent_message=sent_message)
        await state.update_data(selected_filter=filter_name)  # Сохраняем выбранный фильтр в state
        await state.update_data(selected_filter_rus=filter_name_rus)  # Сохраняем выбранный фильтр в state
        await state.set_state(FilterStates.entering_value)  # Устанавливаем состояние


@router.message(FilterStates.entering_value)
async def save_filter_value(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = await state.get_data()  # Получаем данные из state
    filter_name = user_data.get("selected_filter")  # Достаём сохранённый фильтр
    filter_name_rus = user_data.get("selected_filter_rus")
    sented_message = user_data.get("sent_message")  # Достаём отправленное сообщение
    await sented_message.delete()  # Удаляем отправленное сообщение
    filter_value = message.text

    await message.delete() # Удаляем сообщение с введённым значением
    if not filter_name:
        await message.answer("❌ Ошибка: фильтр не найден.")
        return
    
    await update_user_filter(user_id, filter_name, filter_value)  # Сохраняем в БД
    await message.answer(f"✅ Фильтр {filter_name_rus} обновлён: {filter_value}", reply_markup=filter_keyboard_back_button(filter_name=filter_name_rus))
    
    await state.clear()  # Очищаем состояние

@router.callback_query(F.data.startswith("toggle_filter_"))
async def save_filter_value_inline(callback: CallbackQuery):
    try:
        filter_name_rus, value, page = callback.data.split("_")[2:]
        user_id = callback.from_user.id
        filter_name_eng = FILTER_MAPPING_LANGUAGE.get(filter_name_rus)  # Достаём сохранённый фильтр
        
        await update_user_filter(user_id, filter_name_eng, value)  # Сохраняем в БД
        
        current_values = await get_user_filter_values(user_id, filter_name_eng)
        keyboard = filter_keyboard(filter_name_rus, current_values, page=int(page))
        
        await callback.message.edit_reply_markup(reply_markup=keyboard)  # Обновляем клавиатуру
        
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка: {e}")

@router.callback_query(F.data == "check_filters")
async def check_filters(callback: CallbackQuery):
    user_id = callback.from_user.id
    filters_text = await get_user_filters(user_id)
    keyboard = check_filters_keyboard()
    await callback.message.edit_text(filters_text, reply_markup=keyboard, parse_mode="Markdown")

@router.callback_query(F.data.startswith("clear_filter_"))
async def clear_filter(callback: CallbackQuery):
    user_id = callback.from_user.id
    filter_name_rus = callback.data.split("_")[2]
    filter_name = FILTER_MAPPING_LANGUAGE.get(filter_name_rus)  # Перевод в поле модели
    await clear_user_filter(user_id, filter_name)
    filters_text = await get_user_filters_explain()
    
    keyboard = filters_keyboard()
    await callback.message.edit_text(filters_text, reply_markup=keyboard, parse_mode="Markdown")