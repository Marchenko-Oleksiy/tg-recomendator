from aiogram import types, Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from states import SearchStates
from utils import search_movie, search_tv
from keyboards import main_menu_keyboard, media_list_keyboard
from utils.constants import *
from keyboards.keyboards import cancel_keyboard

# Створюємо роутер для обробників пошуку
search_router = Router()

@search_router.message(Command(commands=[SEARCH_COMMAND]))
async def cmd_search(message: types.Message, state: FSMContext):
    """Обробник команди /search"""
    await state.set_state(SearchStates.waiting_for_query)
    await message.answer(
        "Введіть назву фільму або серіалу для пошуку:",
        reply_markup=cancel_keyboard("cancel_search")
    )

@search_router.message(F.text == "🔍 Пошук")
async def text_search(message: types.Message, state: FSMContext):
    """Обробник текстового запиту пошуку"""
    await cmd_search(message, state)

@search_router.message(StateFilter(SearchStates.waiting_for_query))
async def process_search_query(message: types.Message, state: FSMContext):
    """Обробник введеного пошукового запиту"""
    query = message.text.strip()
    
    if not query:
        await message.answer("Будь ласка, введіть коректний запит.")
        return
    
    # Відправляємо повідомлення про пошук
    search_message = await message.answer("🔍 Шукаємо...")
    
    # Пошук фільмів
    movies_result = await search_movie(query)
    
    # Пошук серіалів
    tv_result = await search_tv(query)
    
    # Завершуємо стан
    await state.clear()
    
    # Формуємо результати пошуку
    movie_count = len(movies_result.get("results", [])) if movies_result else 0
    tv_count = len(tv_result.get("results", [])) if tv_result else 0
    
    if movie_count == 0 and tv_count == 0:
        await search_message.edit_text("На жаль, за вашим запитом нічого не знайдено.")
        return
    
    # Формуємо текст з результатами
    text = f"🔍 Результати пошуку за запитом: <b>{query}</b>\n\n"
    
    # Додаємо фільми
    if movie_count > 0:
        text += "<b>🎬 Фільми:</b>\n"
        for i, movie in enumerate(movies_result["results"][:5], 1):
            title = movie.get("title", "Невідома назва")
            release_date = movie.get("release_date", "")
            release_year = f" ({release_date[:4]})" if release_date else ""
            
            rating = movie.get("vote_average", 0)
            rating_stars = "⭐" * int(rating / 2) if rating else ""
            
            text += f"{i}. <b>{title}</b>{release_year} {rating_stars}\n"
        
        if movie_count > 5:
            text += f"... і ще {movie_count - 5} фільмів\n"
        
        text += "\n"
    
    # Додаємо серіали
    if tv_count > 0:
        text += "<b>📺 Серіали:</b>\n"
        for i, tv in enumerate(tv_result["results"][:5], 1):
            title = tv.get("name", "Невідома назва")
            first_air_date = tv.get("first_air_date", "")
            release_year = f" ({first_air_date[:4]})" if first_air_date else ""
            
            rating = tv.get("vote_average", 0)
            rating_stars = "⭐" * int(rating / 2) if rating else ""
            
            text += f"{i}. <b>{title}</b>{release_year} {rating_stars}\n"
        
        if tv_count > 5:
            text += f"... і ще {tv_count - 5} серіалів\n"
    
    await search_message.edit_text(
        text,
        parse_mode="HTML"
    )

@search_router.callback_query(lambda c: c.data == "cancel_search")
async def callback_cancel_search(callback_query: types.CallbackQuery, state: FSMContext):
    """Обробник скасування пошуку"""
    await callback_query.answer()
    await state.clear()
    await callback_query.message.edit_text("Пошук скасовано.")

def register_search_handlers(dp):
    """Реєстрація обробників для пошуку"""
    dp.include_router(search_router) 