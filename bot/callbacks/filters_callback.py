from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramBadRequest

from services.filters_service import update_user_filter, get_user_filters, get_user_filter_values, clear_user_filter, get_user_filters_explain
from keyboards.inline.check_filters_kb import check_filters_keyboard
from keyboards.inline.filters_mapping_kb import filter_keyboard, filter_keyboard_back_button, city_keyboard
from keyboards.inline.filters_kb import filters_keyboard
from .filter_mapping import FILTER_MAPPING_LANGUAGE, FILTER_MAPPING_DESCRIPTION

import logging
logger = logging.getLogger(__name__)

class FilterStates(StatesGroup):
    entering_value = State()
    entering_city = State()

router = Router()

@router.callback_query(F.data.startswith("filter_"))
async def filter_handler(callback: CallbackQuery, state: FSMContext):
    filter_name_rus = callback.data.replace("filter_", "")  # Русское название
    filter_name = FILTER_MAPPING_LANGUAGE.get(filter_name_rus)  # Перевод в поле модели
    filter_description = FILTER_MAPPING_DESCRIPTION.get(filter_name_rus)
    
    if not filter_name:
        await callback.message.answer("❌ Ошибка: фильтр не найден.")
        return
    
    current_values = await get_user_filter_values(callback.from_user.id, filter_name)
    
    # Если это фильтр города, показываем специальную клавиатуру
    if filter_name_rus == "Город":
        keyboard = city_keyboard(current_values)
        await callback.message.edit_text(
            f"Выберите {filter_name_rus} из популярных или введите свой:\n"
            f"Формат: «{filter_description}»",
            reply_markup=keyboard,
        )
        return
    
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
    
    # Получаем информацию о поле из модели
    from users.models import UserFilters
    model_field = UserFilters._meta.get_field(filter_name)
    
    # Проверяем, является ли поле массивом
    from django.contrib.postgres.fields import ArrayField
    if isinstance(model_field, ArrayField):
        # Для полей-массивов разделяем значения по запятой
        if "," in filter_value:
            values = [v.strip() for v in filter_value.split(",")]
            await update_user_filter(user_id, filter_name, values)
        else:
            # Для одиночного значения создаём список с одним элементом
            await update_user_filter(user_id, filter_name, [filter_value])
    else:
        # Для обычных полей сохраняем как есть
        await update_user_filter(user_id, filter_name, filter_value)
    
    await message.answer(f"✅ Фильтр {filter_name_rus} обновлён: {filter_value}", reply_markup=filter_keyboard_back_button(filter_name=filter_name_rus))
    
    await state.clear()  # Очищаем состояние


@router.message(FilterStates.entering_city)
async def save_city_value(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        city = message.text
        logger.info(f"User {user_id} entered city: {city}")
        
        # Получаем данные из состояния
        user_data = await state.get_data()
        message_id = user_data.get("message_id")
        
        # Удаляем сообщение пользователя
        await message.delete()
        
        # Получаем текущие города пользователя
        current_cities = await get_user_filter_values(user_id, "city")
        logger.info(f"Current cities for user {user_id}: {current_cities}")
        
        # Добавляем новый город в список
        if isinstance(current_cities, list):
            if city not in current_cities:
                current_cities.append(city)
        else:
            current_cities = [city]
        
        # Сохраняем обновленный список городов
        await update_user_filter(user_id, "city", current_cities)
        logger.info(f"Updated cities for user {user_id}: {current_cities}")
        
        # Получаем обновленную клавиатуру
        keyboard = city_keyboard(current_cities)
        
        try:
            # Пытаемся обновить исходное сообщение
            await message.bot.edit_message_text(
                chat_id=user_id,
                message_id=message_id,
                text=f"Выберите Город из популярных или введите свой:\nФормат: «москва»\n\n✅ Добавлен город: {city}",
                reply_markup=keyboard
            )
            logger.info(f"Successfully updated message with city keyboard for user {user_id}")
        except TelegramBadRequest as e:
            logger.error(f"Error updating message: {e}")
            # Если сообщение не найдено или не может быть отредактировано, отправляем новое
            await message.answer(
                f"✅ Город добавлен: {city}", 
                reply_markup=filter_keyboard_back_button(filter_name="Город")
            )
        
        # Очищаем состояние
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error in save_city_value: {e}")
        await message.answer(f"❌ Произошла ошибка при сохранении города: {e}")
        await state.clear()


@router.callback_query(F.data.startswith("toggle_filter_"))
async def save_filter_value_inline(callback: CallbackQuery):
    try:
        filter_name_rus, value, _ = callback.data.split("_")[2:]
        user_id = callback.from_user.id
        filter_name_eng = FILTER_MAPPING_LANGUAGE.get(filter_name_rus)  # Достаём сохранённый фильтр
        
        # Получаем текущие значения фильтра
        current_values = await get_user_filter_values(user_id, filter_name_eng)
        
        # Если значение уже выбрано - удаляем его, иначе добавляем
        if value in current_values:
            # Удаляем значение из списка
            if isinstance(current_values, list):
                current_values.remove(value)
        else:
            # Добавляем значение в список
            if not current_values:
                current_values = [value]
            elif isinstance(current_values, list):
                current_values.append(value)
            else:
                current_values = [current_values, value]
        
        await update_user_filter(user_id, filter_name_eng, current_values)  # Сохраняем в БД
        
        keyboard = filter_keyboard(filter_name_rus, current_values, page=1)
        
        await callback.message.edit_reply_markup(reply_markup=keyboard)  # Обновляем клавиатуру
        
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка: {e}")


@router.callback_query(F.data.startswith("toggle_city_"))
async def toggle_city(callback: CallbackQuery):
    try:
        city = callback.data.replace("toggle_city_", "")
        user_id = callback.from_user.id
        logger.info(f"Toggle city {city} for user {user_id}")
        
        # Получаем текущие значения фильтра
        current_values = await get_user_filter_values(user_id, "city")
        logger.info(f"Current city values: {current_values}")
        
        # Если город уже выбран - удаляем его, иначе добавляем
        if city in current_values:
            # Удаляем город из списка
            if isinstance(current_values, list):
                current_values.remove(city)
            else:
                current_values = []
        else:
            # Добавляем город в список
            if not current_values:
                current_values = [city]
            elif isinstance(current_values, list):
                current_values.append(city)
            else:
                current_values = [current_values, city]
        
        logger.info(f"Updated city values: {current_values}")
        
        # Сохраняем обновленный список городов
        await update_user_filter(user_id, "city", current_values)
        
        # Обновляем клавиатуру
        keyboard = city_keyboard(current_values)
        await callback.message.edit_reply_markup(reply_markup=keyboard)
        
        # Показываем уведомление
        await callback.answer(f"{'✅ Город добавлен' if city in current_values else '❌ Город удален'}: {city}")
        
    except Exception as e:
        logger.error(f"Error in toggle_city: {e}")
        await callback.message.answer(f"❌ Ошибка: {e}")


@router.callback_query(F.data == "enter_custom_city")
async def enter_custom_city(callback: CallbackQuery, state: FSMContext):
    try:
        # Сохраняем ID сообщения для дальнейшего обновления
        await state.update_data(message_id=callback.message.message_id)
        await state.update_data(selected_filter="city")
        await state.update_data(selected_filter_rus="Город")
        await state.set_state(FilterStates.entering_city)
        
        logger.info(f"User {callback.from_user.id} is entering custom city, state set to entering_city")
        
        # Показываем всплывающее уведомление
        await callback.answer("Введите название города в чат")
    except Exception as e:
        logger.error(f"Error in enter_custom_city: {e}")
        await callback.message.answer(f"❌ Ошибка: {e}")


@router.callback_query(F.data == "check_filters")
async def check_filters(callback: CallbackQuery):
    user_id = callback.from_user.id
    filters_text = await get_user_filters(user_id)
    keyboard = check_filters_keyboard()
    await callback.message.edit_text(filters_text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data.startswith("clear_filter_"))
async def clear_filter(callback: CallbackQuery):
    try:
        user_id = callback.from_user.id
        filter_name_rus = callback.data.split("_")[2]
        filter_name = FILTER_MAPPING_LANGUAGE.get(filter_name_rus)  # Перевод в поле модели
        
        # Получаем текущие значения перед очисткой
        current_values = await get_user_filter_values(user_id, filter_name)
        logger.info(f"Clearing filter {filter_name} for user {user_id}. Current values: {current_values}")
        
        # Очищаем фильтр
        await clear_user_filter(user_id, filter_name)
        
        # Если это фильтр города, показываем специальную клавиатуру
        if filter_name_rus == "Город":
            try:
                # Получаем новую клавиатуру с пустыми значениями
                keyboard = city_keyboard([])
                
                # Пытаемся изменить текст сообщения, чтобы обойти ошибку "message is not modified"
                await callback.message.edit_text(
                    f"Выберите Город из популярных или введите свой:\nФормат: «москва»\n\n✅ Фильтр по городам очищен",
                    reply_markup=keyboard
                )
            except TelegramBadRequest as e:
                logger.error(f"Error in clear_filter (city): {e}")
                # Если нельзя изменить сообщение, отправляем новое
                await callback.message.delete()
                await callback.message.answer(
                    f"Выберите Город из популярных или введите свой:\nФормат: «москва»\n\n✅ Фильтр по городам очищен",
                    reply_markup=keyboard
                )
            
            # Показываем уведомление
            await callback.answer("✅ Фильтр по городам очищен")
            return
        
        # Для остальных фильтров - стандартное поведение
        filters_text = await get_user_filters_explain()
        keyboard = filters_keyboard()
        await callback.message.edit_text(filters_text, reply_markup=keyboard, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error in clear_filter: {e}")
        await callback.message.answer(f"❌ Ошибка при очистке фильтра: {e}")
        # Возвращаемся к меню фильтров
        filters_text = await get_user_filters_explain()
        keyboard = filters_keyboard()
        await callback.message.edit_text(filters_text, reply_markup=keyboard, parse_mode="Markdown")