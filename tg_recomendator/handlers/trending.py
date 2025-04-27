from aiogram import types, Router, F
from aiogram.filters import Command
from utils import get_trending
from keyboards import media_list_keyboard
from utils.constants import *

# Створюємо роутер для обробників популярних фільмів та серіалів
trending_router = Router()

@trending_router.message(Command(commands=[TRENDING_COMMAND]))
async def cmd_trending(message: types.Message):
    """Обробник команди /trending"""
    # Відправляємо повідомлення про пошук
    search_message = await message.answer("🔍 Отримуємо популярні фільми та серіали...")
    
    # Отримуємо популярні фільми і серіали
    trending_result = await get_trending()
    
    if not trending_result or "results" not in trending_result or not trending_result["results"]:
        await search_message.edit_text("На жаль, не вдалося отримати популярні фільми та серіали.")
        return
    
    # Формуємо текст з результатами
    text = f"🔥 <b>Популярні фільми та серіали (сторінка 1/{trending_result['total_pages']}):</b>\n\n"
    
    for i, item in enumerate(trending_result["results"][:10], 1):
        # Визначаємо тип медіа
        media_type = item.get("media_type", "")
        media_icon = "🎬" if media_type == "movie" else "📺" if media_type == "tv" else "🎭"
        
        # Отримуємо назву фільму/серіалу
        title = item.get("title") or item.get("name", "Невідома назва")
        
        # Отримуємо дату випуску
        release_date = item.get("release_date") or item.get("first_air_date", "")
        release_year = f" ({release_date[:4]})" if release_date else ""
        
        # Отримуємо рейтинг
        rating = item.get("vote_average", 0)
        rating_stars = "⭐" * int(rating / 2) if rating else ""
        
        text += f"{i}. {media_icon} <b>{title}</b>{release_year} {rating_stars}\n"
    
    # Додаємо інлайн клавіатуру для навігації
    keyboard = media_list_keyboard(
        page=1, 
        max_page=min(trending_result["total_pages"], 1000)
    )
    
    await search_message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@trending_router.message(F.text == "🔥 Популярне")
async def text_trending(message: types.Message):
    """Обробник текстового запиту популярних фільмів та серіалів"""
    await cmd_trending(message)

@trending_router.callback_query(lambda c: c.data.startswith("page_") and len(c.data.split("_")) == 2)
async def callback_trending_page(callback_query: types.CallbackQuery):
    """Обробник навігації по сторінках трендів"""
    await callback_query.answer()
    
    # Отримуємо номер сторінки
    page = int(callback_query.data.split("_")[1])
    
    # Отримуємо результати для нової сторінки
    trending_result = await get_trending(page=page)
    
    if not trending_result or "results" not in trending_result or not trending_result["results"]:
        await callback_query.message.edit_text(
            "На жаль, не вдалося отримати популярні фільми та серіали для цієї сторінки.",
        )
        return
    
    # Формуємо текст з результатами
    text = f"🔥 <b>Популярні фільми та серіали (сторінка {page}/{trending_result['total_pages']}):</b>\n\n"
    
    for i, item in enumerate(trending_result["results"][:10], 1):
        # Визначаємо тип медіа
        media_type = item.get("media_type", "")
        media_icon = "🎬" if media_type == "movie" else "📺" if media_type == "tv" else "🎭"
        
        # Отримуємо назву фільму/серіалу
        title = item.get("title") or item.get("name", "Невідома назва")
        
        # Отримуємо дату випуску
        release_date = item.get("release_date") or item.get("first_air_date", "")
        release_year = f" ({release_date[:4]})" if release_date else ""
        
        # Отримуємо рейтинг
        rating = item.get("vote_average", 0)
        rating_stars = "⭐" * int(rating / 2) if rating else ""
        
        text += f"{i}. {media_icon} <b>{title}</b>{release_year} {rating_stars}\n"
    
    # Додаємо інлайн клавіатуру для навігації
    keyboard = media_list_keyboard(
        page=page, 
        max_page=min(trending_result["total_pages"], 1000)
    )
    
    await callback_query.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )

def register_trending_handlers(dp):
    """Реєстрація обробників для популярних фільмів та серіалів"""
    dp.include_router(trending_router) 