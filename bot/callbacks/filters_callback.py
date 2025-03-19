from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import State, StatesGroup

from services.filters_service import update_user_filter, get_user_filters
from keyboards.inline.check_filters_kb import check_filters_keyboard
from keyboards.inline.filters_mapping_kb import filter_keyboard
from .filter_mapping import FILTER_MAPPING_LANGUAGE, FILTER_MAPPING_DESCRIPTION


class FilterStates(StatesGroup):
    entering_value = State()

router = Router()

@router.callback_query(F.data.startswith("filter_"))
async def filter_handler(callback: CallbackQuery, state: FSMContext):
    # Проверяем, есть ли сохранённое сообщение с запросом и удаляем его, если оно существует
    data = await state.get_data()
    old_message = data.get("sent_message")
    if old_message:
        await old_message.delete()

    filter_name_rus = callback.data.replace("filter_", "")  # Русское название
    filter_name = FILTER_MAPPING_LANGUAGE.get(filter_name_rus)  # Перевод в поле модели
    filter_description = FILTER_MAPPING_DESCRIPTION.get(filter_name_rus)

    if not filter_name:
        await callback.message.answer("❌ Ошибка: фильтр не найден.")
        return
    keyboard = filter_keyboard(filter_name_rus)
    await state.update_data(selected_filter=filter_name)  # Сохраняем выбранный фильтр в state
    await state.update_data(selected_filter_rus=filter_name_rus)  # Сохраняем выбранный фильтр в state
    sent_message = await callback.message.answer(
        f"Введите значение для {filter_name_rus}\n"
        f"Формат: «{filter_description}»",
        reply_markup=keyboard
    )
    await state.update_data(sent_message=sent_message)
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
    await message.answer(f"✅ Фильтр {filter_name_rus} обновлён: {filter_value}")
    
    await state.clear()  # Очищаем состояние

@router.callback_query(F.data.startswith("value_filter_"))
async def save_filter_value_inline(callback: CallbackQuery, state: FSMContext):
    try:
        user_id = callback.from_user.id
        user_data = await state.get_data()  # Получаем данные из state
        filter_name = user_data.get("selected_filter")  # Достаём сохранённый фильтр
        filter_name_rus = user_data.get("selected_filter_rus")
        sented_message = user_data.get("sent_message")  # Достаём отправленное сообщение
        await sented_message.delete()  # Удаляем отправленное сообщение
        filter_value = callback.data.replace(f"value_filter_{filter_name_rus}_", "")
        
        await update_user_filter(user_id, filter_name, filter_value)  # Сохраняем в БД
        await callback.message.answer(f"✅ Фильтр {filter_name_rus} обновлён: {filter_value}")
        
        await state.clear()  # Очищаем состояние
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка: {e}")

@router.callback_query(F.data == "check_filters")
async def check_filters(callback: CallbackQuery):
    user_id = callback.from_user.id
    filters_text = await get_user_filters(user_id)
    keyboard = check_filters_keyboard()
    await callback.message.edit_text(filters_text, reply_markup=keyboard, parse_mode="Markdown")
    