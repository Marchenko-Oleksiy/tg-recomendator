from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from utils import db
from keyboards import main_menu_keyboard
from utils.constants import *

# Створюємо роутер для обробників загальних команд
common_router = Router()

@common_router.message(Command(commands=[START_COMMAND]))
async def cmd_start(message: types.Message, state: FSMContext):
    """Обробник команди /start"""
    # Скидаємо будь-який попередній стан
    await state.clear()
    
    # Додаємо або оновлюємо інформацію про користувача
    user = message.from_user
    db.add_user(user.id, user.username, user.first_name, user.last_name)
    
    welcome_text = (
        f"👋 Вітаю, {user.first_name}!\n\n"
        f"Я бот, який допоможе знайти фільми, серіали та мультсеріали для перегляду.\n\n"
        f"Використовуйте кнопки меню для навігації."
    )
    await message.answer(welcome_text, reply_markup=main_menu_keyboard())

@common_router.message(Command(commands=[HELP_COMMAND]))
@common_router.message(F.text == "❓ Допомога")
async def cmd_help(message: types.Message):
    """Обробник команди /help"""
    help_text = (
        "🔍 <b>Як користуватись ботом:</b>\n\n"
        "• <b>Категорії</b> - перегляд фільмів/серіалів за категоріями та жанрами\n"
        "• <b>Пошук</b> - пошук за назвою\n"
        "• <b>Популярне</b> - отримати список популярних фільмів та серіалів\n\n"
        "📝 <b>Доступні команди:</b>\n"
        "/start - запустити бота\n"
        "/help - отримати довідку\n"
        "/categories - перегляд категорій\n"
        "/trending - популярні фільми і серіали\n"
        "/search - пошук за назвою\n"
    )
    await message.answer(help_text, parse_mode="HTML")

@common_router.message(F.text == "🔙 Назад до меню")
async def process_back_to_menu(message: types.Message, state: FSMContext):
    """Обробник кнопки повернення до головного меню"""
    await state.clear()
    await message.answer("Повертаємось до головного меню", reply_markup=main_menu_keyboard())

def register_common_handlers(dp):
    """Реєстрація обробників загальних команд"""
    dp.include_router(common_router) 