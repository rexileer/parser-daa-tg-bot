from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import State, StatesGroup

from services.filters_service import update_user_filter
from .filter_mapping import FILTER_MAPPING


class FilterStates(StatesGroup):
    entering_value = State()

router = Router()

@router.callback_query(F.data.startswith("filter_"))
async def filter_handler(callback: CallbackQuery, state: FSMContext):
    filter_name_rus = callback.data.replace("filter_", "")  # Русское название
    filter_name = FILTER_MAPPING.get(filter_name_rus)  # Перевод в поле модели

    if not filter_name:
        await callback.message.answer("❌ Ошибка: фильтр не найден.")
        return
    await state.update_data(selected_filter=filter_name)  # Сохраняем выбранный фильтр в state
    await callback.message.answer(f"Введите значение для {filter_name}:")
    await state.set_state(FilterStates.entering_value)  # Устанавливаем состояние


@router.message(FilterStates.entering_value)
async def save_filter_value(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = await state.get_data()  # Получаем данные из state
    filter_name = user_data.get("selected_filter")  # Достаём сохранённый фильтр
    filter_value = message.text

    if not filter_name:
        await message.answer("❌ Ошибка: фильтр не найден.")
        return
    
    await update_user_filter(user_id, filter_name, filter_value)  # Сохраняем в БД
    await message.answer(f"✅ Фильтр {filter_name} обновлён: {filter_value}")
    
    await state.clear()  # Очищаем состояние
