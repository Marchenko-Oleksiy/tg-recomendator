from aiogram import Router, F, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from utils.constants import *

from states import SearchStates
from utils import search_movie, search_tv
from keyboards import media_list_keyboard, main_menu_keyboard
from keyboards import cancel_keyboard

search_router = Router()
@search_router.message(Command(commands=[SEARCH_COMMAND]))
async def cmd_search(message: types.Message, state: FSMContext):
    """Обробник команди /search"""
    await state.set_state(SearchStates.waiting_for_query)
    await message.answer(
        "Введіть назву фільму або серіалу для пошуку:",
        reply_markup=cancel_keyboard("cancel_search")
    )

@search_router.message(F.text == "🔎 Пошук")
async def text_search(message: types.Message, state: FSMContext):
    await cmd_search(message, state)
    
@search_router.message(StateFilter(SearchStates.waiting_for_query))
async def process_query(message: types.Message, state: FSMContext):
    query = message.text.strip()
    if not query:
        await message.answer("Будь ласка, введіть назву фільму або серіалу для пошуку.")
        return
    
    search_message = await message.answer("🔎 Пошук...")
    movies_result = await search_movie(query)
    tv_result = await search_tv(query)
    
    await state.clear()
    
    movie_count = len(movies_result.get('results', [])) if movies_result else 0
    tv_count = len(tv_result.get('results', [])) if tv_result else 0
    
    if movie_count == 0 and tv_count == 0:
        await search_message.edit_text("🔎 Нічого не знайдено. Спробуйте ще раз.")
        return
    
    text = f"🎬 Результати пошуку за запитом <b>{query}</b>:\n\n"
    
    if movie_count > 0:
        text += f"📺 <b>{movie_count}</b> фільмів знайдено:\n"
        for i, movie in enumerate(movies_result['results'][:5], 1):
            title = movie.get('title', movie.get('title', 'Невідома назва'))
            release_date = movie.get('release_date', '')
            release_year = f'({release_date[:4]})' if release_date else ''
            rating = movie.get('vote_average', 0)
            rating_stars = '⭐' * int(rating / 2) if rating else ''
            text += f"{i}. <b>{title}</b> {release_year} {rating_stars}\n"
            
    if tv_count > 5:
        text += f"... і ще {tv_count-5} фільмів\n"    
        
    text += "\n"
    
    if tv_count > 0:
        text += f"📺 <b>{tv_count}</b> серіалів знайдено:\n"
        for i, tv in enumerate(tv_result['results'][:5], 1):
            title = tv.get('name', 'Невідома назва')
            first_air_date = tv.get('first_air_date', '')
            release_date = f'({first_air_date[:4]})' if first_air_date else ''
            rating = tv.get('vote_average', 0)
            rating_stars = '⭐' * int(rating / 2) if rating else ''
            text += f"{i}. <b>{title}</b> {release_date} {rating_stars}\n"
            
    if tv_count > 5:
        text += f"... і ще {tv_count-5} серіалів\n"
            
    await search_message.edit_text(text, parse_mode='HTML')
    
@search_router.callback_query(lambda c: c.data == "cancel_search")
async def cancel_search(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await state.clear()
    await callback_query.message.edit_text("🔎 Пошук скасовано.")
    
def register_search_handlers(dp):
    dp.include_router(search_router)