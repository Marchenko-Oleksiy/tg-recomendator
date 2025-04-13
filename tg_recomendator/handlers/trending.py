from aiogram import types, Router, F  
from aiogram.filters import Command 
from keyboards import media_list_keyboard
from utils.constants import *

trending_router = Router()

@trending_router.message(Command(commands=[TRENDING_COMMAND]))
async def trending_command(message: types.Message):
    search_message = await message.answer('🔎 Отримуємо популярні фільми та серіали...')
    
    trending_result = await get_trending()

    if not trending_result or "results" not in trending_result or not trending_result["results"]:
        await search_message.edit_text("На жаль, не вдалося знайти популярні фільми та серіали.")
        return
    
    text = f"🔥 <b>Популярні фільми та серіали (сторінка 1/{trending_result['total_pages']}):</b>\n\n"
    
    for i, item in enumerate(trending_result["results"][:10], 1):
        media_type = item.get("media_type", "")
        media_icon = "🎬" if media_type == "movie" else "📺" if media_type == "tv" else "🎭"
        
        title = item.get('title')or  item.get('name', 'Невідома назва')
        release_date = item.get('release_date', item.get('first_air_date', 'Невідома дата'))
        release_year = release_date[:4] if len(release_date) > 4 else release_date
        rating = item.get('vote_average', 0)

        text += f"{media_icon} <b>{title}</b> ({release_year}) - {rating:.1f}\n"

    keyboard = media_list_keyboard(
        page=1,
        max_page=min(trending_result['total_pages'], 1000),
    )
    
    await search_message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    
@trending_router.message(F.text == "🔥 Популярне")
async def text_trending(message: types.Message):
    await trending_command(message)
    

@trending_router.callback_query(lambda c: c.data.startswith("page_") and len(c.data.split("_")) == 2)
async def page_callback(callback_query: types.CallbackQuery):
    await callback_query.answer()
    
    page = int(callback_query.data.split("_")[1])
    trending_result = await get_trending(page=page)
    
    if not trending_result or "results" not in trending_result or not trending_result["results"]:
        await callback_query.message.answer("На жаль, не вдалося знайти популярні фільми та серіали.")
        return
    
    text = f"🔥 <b>Популярні фільми та серіали (сторінка {page}/{trending_result['total_pages']}):</b>\n\n"
    
    for i, item in enumerate(trending_result["results"][:10], 1):
        media_type = item.get("media_type", "")
        media_icon = "🎬" if media_type == "movie" else "📺" if media_type == "tv" else "🎭"
        
        title = item.get('title') or item.get('name', 'Невідома назва')
        release_date = item.get('release_date', item.get('first_air_date', 'Невідома дата'))
        release_year = f" ({release_date[:4]})" if release_date else ""
        rating = item.get('vote_average', 0)
        rating_stars= "⭐" * int(rating / 2 ) if rating > 0 else ""
        
        text += f"{i}. {media_icon} <b>{title}</b>{release_year} {rating_stars}\n"

    keyboard = media_list_keyboard(
        page=page,
        max_page=min(trending_result['total_pages'], 1000),
    )
    
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        

def register_trending_handlers(dp):
    dp.include_router(trending_router)
