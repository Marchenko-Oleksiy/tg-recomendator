from aiogram import types, Router, F
from aiogram import exceptions
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import logging
from utils import db, get_genres, discover_by_genre
from keyboards import categories_inline_keyboard, genres_inline_keyboard, media_list_keyboard
from utils.constants import *

# Створюємо роутер для обробників категорій
categories_router = Router()

@categories_router.message(Command(commands=[CATEGORIES_COMMAND]))
async def cmd_categories(message: types.Message):
    """Обробник команди /categories"""
    categories = db.get_categories()
    
    if not categories:
        await message.answer("На жаль, категорії не знайдено.")
        return
    
    await message.answer(
        "Оберіть категорію:",
        reply_markup=categories_inline_keyboard(categories)
    )

@categories_router.message(F.text == "🎬 Категорії")
async def text_categories(message: types.Message):
    """Обробник текстового запиту категорій"""
    await cmd_categories(message)

@categories_router.callback_query(lambda c: c.data.startswith("category_"))
async def callback_category_selected(callback_query: types.CallbackQuery):
    """Обробник вибору категорії"""
    await callback_query.answer()
    
    # Отримуємо ID категорії з даних callback_query
    category_id = int(callback_query.data.split("_")[1])
    
    # Отримуємо жанри для цієї категорії
    genres = db.get_genres(category_id)
    
    # Якщо жанрів немає в базі, отримуємо з API
    if not genres:
        # Визначаємо тип медіа для запиту до API
        if category_id == 1:  # Фільми
            media_type = MOVIE
        elif category_id == 2:  # Серіали
            media_type = TV
        elif category_id == 3:  # Мультфільми
            # Для мультфільмів будемо використовувати режим фільмів
            # і додаткові фільтри в подальшому
            media_type = MOVIE
        else:
            media_type = MOVIE  # За замовчуванням
        
        # Отримуємо жанри з API
        api_genres = await get_genres(media_type)
        
        if api_genres and "genres" in api_genres:
            for genre in api_genres["genres"]:
                # Додаємо жанри до бази даних
                db.add_genre(genre["name"], genre["id"], category_id)
            
            # Оновлюємо список жанрів
            genres = db.get_genres(category_id)
        
            # Для мультфільмів, додатково додамо жанр анімації, якщо його немає
            if category_id == 3 and api_genres["genres"]:
                # ID для жанру анімації в TMDB API
                animation_genre_id = 16  # "Animation" жанр у TMDB
                
                # Перевіряємо, чи є вже цей жанр у базі
                has_animation_genre = False
                for genre in genres:
                    if genre["api_id"] == animation_genre_id:
                        has_animation_genre = True
                        break
                
                # Якщо немає, додаємо
                if not has_animation_genre:
                    db.add_genre("Анімація", animation_genre_id, category_id)
                    # Оновлюємо список жанрів
                    genres = db.get_genres(category_id)
    
    if not genres:
        text = "На жаль, жанри для цієї категорії не знайдено."
        markup = categories_inline_keyboard(db.get_categories())
    else:
        text = "Оберіть жанр:"
        markup = genres_inline_keyboard(genres, category_id)
    
    try:
        await callback_query.message.edit_text(text, reply_markup=markup)
    except exceptions.TelegramBadRequest as e:
        if "message is not modified" in str(e):
            # Повідомлення не змінено, ігноруємо
            pass
        elif "message to edit not found" in str(e):
            # Повідомлення не знайдено, створюємо нове
            await callback_query.message.answer(text, reply_markup=markup)
        else:
            # Інші помилки перевидаємо
            raise

@categories_router.callback_query(lambda c: c.data.startswith("genre_"))
async def callback_genre_selected(callback_query: types.CallbackQuery):
    """Обробник вибору жанру"""
    await callback_query.answer()
    
    # Отримуємо ID жанру і категорії з даних callback_query
    _, genre_id, category_id = callback_query.data.split("_")
    genre_id = int(genre_id)
    category_id = int(category_id)
    
    # Визначаємо тип медіа за категорією
    if category_id == 1:  # Фільми
        media_type = MOVIE
    elif category_id == 2:  # Серіали
        media_type = TV
    elif category_id == 3:  # Мультфільми
        media_type = MOVIE  # Будемо використовувати тип фільмів для мультфільмів
    else:
        media_type = MOVIE  # За замовчуванням
    
    # Отримуємо API_ID для жанру
    genres = db.get_genres(category_id)
    api_genre_id = None
    
    for genre in genres:
        if genre["id"] == genre_id:
            api_genre_id = genre["api_id"]
            break
    
    if not api_genre_id:
        text = "Помилка: жанр не знайдено."
        markup = genres_inline_keyboard(genres, category_id)
        try:
            await callback_query.message.edit_text(text, reply_markup=markup)
        except exceptions.TelegramBadRequest as e:
            if "message is not modified" in str(e):
                pass
            elif "message to edit not found" in str(e):
                await callback_query.message.answer(text, reply_markup=markup)
            else:
                raise
        return
    
    # Отримуємо фільми/серіали за жанром з API
    # Для категорії "Мультфільми" додаємо анімаційний жанр у запит
    if category_id == 3:  # Мультфільми
        animation_genre_id = 16  # ID жанру "Animation" у TMDB
        # Якщо вже обраний жанр анімації, не треба додавати додатковий фільтр
        if api_genre_id != animation_genre_id:
            # Тут ми вказуємо обидва жанри для пошуку
            result = await discover_by_genre(media_type, f"{animation_genre_id},{api_genre_id}", page=1)
        else:
            result = await discover_by_genre(media_type, api_genre_id, page=1)
    else:
        result = await discover_by_genre(media_type, api_genre_id, page=1)
    
    if not result or "results" not in result or not result["results"]:
        text = "На жаль, не знайдено фільмів/серіалів за обраним жанром."
        markup = genres_inline_keyboard(genres, category_id)
        try:
            await callback_query.message.edit_text(text, reply_markup=markup)
        except exceptions.TelegramBadRequest as e:
            if "message is not modified" in str(e):
                pass
            elif "message to edit not found" in str(e):
                await callback_query.message.answer(text, reply_markup=markup)
            else:
                raise
        return
    
    # Формуємо текст з результатами
    text = f"Результати пошуку (сторінка 1/{result['total_pages']}):\n\n"
    
    for i, item in enumerate(result["results"][:10], 1):
        title = item.get("title") or item.get("name", "Невідома назва")
        release_date = item.get("release_date") or item.get("first_air_date", "")
        release_year = f" ({release_date[:4]})" if release_date else ""
        
        rating = item.get("vote_average", 0)
        rating_stars = "⭐" * int(rating / 2) if rating else ""
        
        text += f"{i}. <b>{title}</b>{release_year} {rating_stars}\n"
    
    # Додаємо інлайн клавіатуру для навігації
    keyboard = media_list_keyboard(
        page=1, 
        max_page=min(result["total_pages"], 1000), 
        media_type=media_type, 
        genre_id=api_genre_id if category_id != 3 else f"{animation_genre_id},{api_genre_id}" if api_genre_id != 16 else "16"
    )
    
    try:
        await callback_query.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    except exceptions.TelegramBadRequest as e:
        if "message is not modified" in str(e):
            pass
        elif "message to edit not found" in str(e):
            await callback_query.message.answer(text, reply_markup=keyboard, parse_mode="HTML")
        else:
            raise

@categories_router.callback_query(lambda c: c.data == "back_to_categories")
async def callback_back_to_categories(callback_query: types.CallbackQuery):
    """Обробник повернення до категорій"""
    await callback_query.answer()
    
    categories = db.get_categories()
    
    try:
        await callback_query.message.edit_text(
            "Оберіть категорію:",
            reply_markup=categories_inline_keyboard(categories)
        )
    except exceptions.TelegramBadRequest as e:
        if "message is not modified" in str(e):
            pass
        elif "message to edit not found" in str(e):
            await callback_query.message.answer("Оберіть категорію:", reply_markup=categories_inline_keyboard(categories))
        else:
            raise

@categories_router.callback_query(lambda c: c.data == "back_to_main")
async def callback_back_to_main(callback_query: types.CallbackQuery):
    """Обробник повернення до головного меню"""
    await callback_query.answer()
    try:
        await callback_query.message.delete()
    except Exception as e:
        logging.error(f"Помилка при видаленні повідомлення: {e}")
    await callback_query.message.answer("Головне меню")

@categories_router.callback_query(lambda c: c.data.startswith("page_") and len(c.data.split("_")) > 2)
async def callback_page_navigation(callback_query: types.CallbackQuery):
    """Обробник навігації по сторінках результатів"""
    await callback_query.answer()
    
    # Парсимо дані callback_query
    parts = callback_query.data.split("_")
    page = int(parts[1])
    
    media_type = None
    genre_id = None
    
    if len(parts) > 2:
        media_type = parts[2]
    
    if len(parts) > 3:
        genre_id = parts[3]  # Може містити кілька ID через кому
    
    if not media_type or not genre_id:
        text = "Помилка: недостатньо даних для навігації."
        markup = None
        try:
            await callback_query.message.edit_text(text, reply_markup=markup)
        except exceptions.TelegramBadRequest as e:
            if "message is not modified" in str(e):
                pass
            elif "message to edit not found" in str(e):
                await callback_query.message.answer(text)
            else:
                raise
        return
    
    # Отримуємо результати для нової сторінки
    result = await discover_by_genre(media_type, genre_id, page=page)
    
    if not result or "results" not in result or not result["results"]:
        text = "На жаль, не знайдено фільмів/серіалів для цієї сторінки."
        markup = None
        try:
            await callback_query.message.edit_text(text, reply_markup=markup)
        except exceptions.TelegramBadRequest as e:
            if "message is not modified" in str(e):
                pass
            elif "message to edit not found" in str(e):
                await callback_query.message.answer(text)
            else:
                raise
        return
    
    # Формуємо текст з результатами
    text = f"Результати пошуку (сторінка {page}/{result['total_pages']}):\n\n"
    
    for i, item in enumerate(result["results"][:10], 1):
        title = item.get("title") or item.get("name", "Невідома назва")
        release_date = item.get("release_date") or item.get("first_air_date", "")
        release_year = f" ({release_date[:4]})" if release_date else ""
        
        rating = item.get("vote_average", 0)
        rating_stars = "⭐" * int(rating / 2) if rating else ""
        
        text += f"{i}. <b>{title}</b>{release_year} {rating_stars}\n"
    
    # Додаємо інлайн клавіатуру для навігації
    keyboard = media_list_keyboard(
        page=page, 
        max_page=min(result["total_pages"], 1000), 
        media_type=media_type, 
        genre_id=genre_id
    )
    
    try:
        await callback_query.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    except exceptions.TelegramBadRequest as e:
        if "message is not modified" in str(e):
            pass
        elif "message to edit not found" in str(e):
            await callback_query.message.answer(text, reply_markup=keyboard, parse_mode="HTML")
        else:
            raise

@categories_router.callback_query(lambda c: c.data.startswith("back_to_genres_"))
async def callback_back_to_genres(callback_query: types.CallbackQuery):
    """Обробник повернення до жанрів"""
    await callback_query.answer()
    
    # Отримуємо тип медіа з даних callback_query
    media_type = callback_query.data.split("_")[-1]
    
    # Визначаємо ID категорії за типом медіа
    category_id = 1  # За замовчуванням - фільми
    
    if media_type == TV:
        category_id = 2
    elif media_type == ANIMATION:
        category_id = 3
    
    # Отримуємо жанри для цієї категорії
    genres = db.get_genres(category_id)
    
    try:
        await callback_query.message.edit_text(
            "Оберіть жанр:",
            reply_markup=genres_inline_keyboard(genres, category_id)
        )
    except exceptions.TelegramBadRequest as e:
        if "message is not modified" in str(e):
            pass
        elif "message to edit not found" in str(e):
            await callback_query.message.answer("Оберіть жанр:", reply_markup=genres_inline_keyboard(genres, category_id))
        else:
            raise

def register_categories_handlers(dp):
    """Реєстрація обробників для категорій та жанрів"""
    dp.include_router(categories_router) 