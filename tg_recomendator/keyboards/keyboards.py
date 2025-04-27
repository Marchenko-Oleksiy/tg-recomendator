from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from utils.constants import *

# Головне меню
def main_menu_keyboard():
    buttons = [
        [KeyboardButton(text="🎬 Категорії")],
        [KeyboardButton(text="🔍 Пошук")],
        [KeyboardButton(text="🔥 Популярне")],
        [KeyboardButton(text="❓ Допомога")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return keyboard

# Клавіатура для Адміністратора
def admin_keyboard():
    buttons = [
        [KeyboardButton(text="➕ Додати категорію")],
        [KeyboardButton(text="➕ Додати жанр")],
        [KeyboardButton(text="➕ Додати фільм/серіал")],
        [KeyboardButton(text="🔙 Назад до меню")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return keyboard

# Інлайн клавіатура для категорій
def categories_inline_keyboard(categories):
    buttons = []
    
    for category in categories:
        buttons.append([
            InlineKeyboardButton(
                text=category["name"], 
                callback_data=f"category_{category['id']}"
            )
        ])
    
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

# Інлайн клавіатура для жанрів
def genres_inline_keyboard(genres, category_id):
    buttons = []
    
    for genre in genres:
        buttons.append([
            InlineKeyboardButton(
                text=genre["name"], 
                callback_data=f"genre_{genre['id']}_{category_id}"
            )
        ])
    
    buttons.append([InlineKeyboardButton(text="🔙 До категорій", callback_data="back_to_categories")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

# Інлайн клавіатура для списку фільмів/серіалів
def media_list_keyboard(page=1, max_page=1, media_type=None, genre_id=None):
    buttons = []
    
    navigation = []
    
    if page > 1:
        prev_page = f"page_{page-1}"
        if media_type:
            prev_page += f"_{media_type}"
        if genre_id:
            prev_page += f"_{genre_id}"
        navigation.append(InlineKeyboardButton(text="⬅️", callback_data=prev_page))
    
    navigation.append(InlineKeyboardButton(text=f"{page}/{max_page}", callback_data="current_page"))
    
    if page < max_page:
        next_page = f"page_{page+1}"
        if media_type:
            next_page += f"_{media_type}"
        if genre_id:
            next_page += f"_{genre_id}"
        navigation.append(InlineKeyboardButton(text="➡️", callback_data=next_page))
    
    buttons.append(navigation)
    
    if genre_id:
        buttons.append([InlineKeyboardButton(text="🔙 До жанрів", callback_data=f"back_to_genres_{media_type}")])
    else:
        buttons.append([InlineKeyboardButton(text="🔙 До категорій", callback_data="back_to_categories")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

# Інлайн клавіатура для деталей фільму/серіалу
def media_details_keyboard(media_id, media_type):
    buttons = [
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"back_to_list_{media_type}")]
    ]
    
    # Кнопка для перегляду трейлера, можливо реалізувати пізніше
    # buttons.append([InlineKeyboardButton(text="🎬 Дивитися трейлер", callback_data=f"trailer_{media_id}_{media_type}")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

# Інлайн клавіатура для вибору типу медіа при додаванні
def media_type_keyboard():
    buttons = [
        [InlineKeyboardButton(text="🎬 Фільм", callback_data=f"add_media_movie")],
        [InlineKeyboardButton(text="📺 Серіал", callback_data=f"add_media_tv")],
        [InlineKeyboardButton(text="🧸 Мультфільм", callback_data=f"add_media_animation")],
        [InlineKeyboardButton(text="🔙 Скасувати", callback_data=f"cancel_add_media")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

# Інлайн клавіатура для скасування операції
def cancel_keyboard(callback_data="cancel"):
    buttons = [
        [InlineKeyboardButton(text="❌ Скасувати", callback_data=callback_data)]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard 