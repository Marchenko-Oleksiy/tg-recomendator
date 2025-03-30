from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

from utils.constants import *

def main_menu_keyboard():
    buttons = [
        [KeyboardButton(text="🎭 Категорії"), KeyboardButton(text="🔎 Пошук")],
        [KeyboardButton(text="🔥 Популярне"), KeyboardButton(text="❓ Допомога")]
    ]
    
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return keyboard

def admin_keybard():
    buttons = [
        [KeyboardButton(text="➕ Додати категорію"), 
         KeyboardButton(text="➕ Додати жанр")],
        [KeyboardButton(text="➕ Додати фільм/серіал"), 
         KeyboardButton(text="🔙 Назад до меню")]
    ]
    
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return keyboard

def categories_inline_keyboard(categories):
    buttons = []
    for category in categories:
        buttons.append(
            InlineKeyboardButton(text=category["name"],
                                 callback_data=f'category_{category["id"]}')
        )
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

