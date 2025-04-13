from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from utils import db 
from keyboards.keyboards import main_menu_keyboard
from utils.constants import *


common_router = Router()

@common_router.message(Command(commands=[START_COMMAND]))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear() 
    
    user = message.from_user
    db.add_user(user.id, user.username, user.first_name, user.last_name)
    
    welcome_text = (
        f"👋 Привіт, {user.first_name}!\n\n"
        f"🎬 Вітаємо в нашому  боті Рекомендаторі для перегляду фільмів та серіалів!\n\n"
        f"🎈 Ось що я можу для тебе зробити:\n\n"
        f"🔍 Пошук фільмів та серіалів за категоріями та жанрами\n"
        f"🔍 Перегляд трендових фільмів та серіалів\n"
        f"🔍 Додавання власних фільмів та серіалів для перегляду\n\n"
        f"Використовуйте кнопки меню для навігації."
    )
    
    await message.answer(welcome_text, reply_markup=main_menu_keyboard)

@common_router.message(Command(commands=[HELP_COMMAND]))
@common_router.message(F.text == "❓Допомога")
async def cmd_help(message: types.Message):
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

@common_router.message(F.text == "🔙Назад до меню")
async def back_to_main(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Повертаємось до головного меню", 
                         reply_markup=main_menu_keyboard())


def register_common_handlers(dp):
    dp.include_router(common_router)
