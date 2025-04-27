from aiogram import types, Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from states import AdminStates
from utils import db
from keyboards import admin_keyboard, main_menu_keyboard, categories_inline_keyboard, media_type_keyboard
from utils.constants import *

# Створюємо роутер для обробників адміністративних функцій
admin_router = Router()

@admin_router.message(Command(commands=[ADMIN_COMMAND]))
async def cmd_admin(message: types.Message, state: FSMContext):
    """Обробник команди /admin"""
    user_id = message.from_user.id
    
    # Перевіряємо, чи користувач є адміністратором
    if not db.is_admin(user_id):
        # Перевіряємо, чи є вже адміністратори в системі
        db.connect()
        db.cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = 1")
        admin_count = db.cursor.fetchone()[0]
        db.disconnect()
        
        # Якщо адміністраторів немає, робимо першого користувача адміністратором
        if admin_count == 0:
            db.make_admin(user_id)
            await message.answer("Ви стали першим адміністратором бота.")
        else:
            await message.answer("У вас немає прав для доступу до адміністративної панелі.")
            return
    
    await state.set_state(AdminStates.waiting_for_command)
    await message.answer(
        "Адміністративна панель. Оберіть дію:",
        reply_markup=admin_keyboard()
    )

@admin_router.message(StateFilter(AdminStates.waiting_for_command), F.text == "➕ Додати категорію")
async def process_add_category(message: types.Message, state: FSMContext):
    """Обробник додавання категорії"""
    await state.set_state(AdminStates.waiting_for_category_name)
    await message.answer("Введіть назву нової категорії:")

@admin_router.message(StateFilter(AdminStates.waiting_for_category_name))
async def process_category_name(message: types.Message, state: FSMContext):
    """Обробник введення назви категорії"""
    category_name = message.text.strip()
    
    if not category_name:
        await message.answer("Будь ласка, введіть коректну назву категорії.")
        return
    
    # Зберігаємо назву категорії в стані
    await state.update_data(category_name=category_name)
    
    await state.set_state(AdminStates.waiting_for_category_description)
    await message.answer("Введіть опис категорії (або натисніть /skip для пропуску):")

@admin_router.message(StateFilter(AdminStates.waiting_for_category_description))
async def process_category_description(message: types.Message, state: FSMContext):
    """Обробник введення опису категорії"""
    description = message.text.strip()
    
    if message.text == "/skip":
        description = ""
    
    # Отримуємо дані зі стану
    data = await state.get_data()
    category_name = data.get("category_name")
    
    # Додаємо категорію до бази даних
    success = db.add_category(category_name, description)
    
    if success:
        await message.answer(f"Категорія '{category_name}' успішно додана.")
    else:
        await message.answer(f"Категорія з назвою '{category_name}' вже існує.")
    
    # Повертаємось до адмін-меню
    await state.set_state(AdminStates.waiting_for_command)
    await message.answer(
        "Оберіть наступну дію:",
        reply_markup=admin_keyboard()
    )

@admin_router.message(StateFilter(AdminStates.waiting_for_command), F.text == "➕ Додати жанр")
async def process_add_genre(message: types.Message, state: FSMContext):
    """Обробник додавання жанру"""
    await state.set_state(AdminStates.waiting_for_genre_name)
    await message.answer("Введіть назву нового жанру:")

@admin_router.message(StateFilter(AdminStates.waiting_for_genre_name))
async def process_genre_name(message: types.Message, state: FSMContext):
    """Обробник введення назви жанру"""
    genre_name = message.text.strip()
    
    if not genre_name:
        await message.answer("Будь ласка, введіть коректну назву жанру.")
        return
    
    # Зберігаємо назву жанру в стані
    await state.update_data(genre_name=genre_name)
    
    await state.set_state(AdminStates.waiting_for_genre_api_id)
    await message.answer("Введіть API ID жанру (число):")

@admin_router.message(StateFilter(AdminStates.waiting_for_genre_api_id))
async def process_genre_api_id(message: types.Message, state: FSMContext):
    """Обробник введення API ID жанру"""
    try:
        api_id = int(message.text.strip())
    except ValueError:
        await message.answer("Будь ласка, введіть коректний API ID (ціле число).")
        return
    
    # Зберігаємо API ID жанру в стані
    await state.update_data(genre_api_id=api_id)
    
    # Отримуємо категорії
    categories = db.get_categories()
    
    if not categories:
        await message.answer("Спершу додайте хоча б одну категорію.")
        await state.set_state(AdminStates.waiting_for_command)
        return
    
    await state.set_state(AdminStates.waiting_for_genre_category)
    
    # Формуємо текст з категоріями
    text = "Оберіть категорію для жанру:\n\n"
    for i, category in enumerate(categories, 1):
        text += f"{i}. {category['name']}\n"
    
    await message.answer(text)

@admin_router.message(StateFilter(AdminStates.waiting_for_genre_category))
async def process_genre_category(message: types.Message, state: FSMContext):
    """Обробник вибору категорії для жанру"""
    try:
        category_index = int(message.text.strip()) - 1
    except ValueError:
        await message.answer("Будь ласка, введіть коректний номер категорії.")
        return
    
    # Отримуємо категорії
    categories = db.get_categories()
    
    if not categories or category_index < 0 or category_index >= len(categories):
        await message.answer("Категорія з таким номером не знайдена.")
        return
    
    category_id = categories[category_index]["id"]
    
    # Отримуємо дані зі стану
    data = await state.get_data()
    genre_name = data.get("genre_name")
    genre_api_id = data.get("genre_api_id")
    
    # Додаємо жанр до бази даних
    success = db.add_genre(genre_name, genre_api_id, category_id)
    
    if success:
        await message.answer(f"Жанр '{genre_name}' успішно доданий до категорії '{categories[category_index]['name']}'.")
    else:
        await message.answer(f"Жанр з назвою '{genre_name}' вже існує.")
    
    # Повертаємось до адмін-меню
    await state.set_state(AdminStates.waiting_for_command)
    await message.answer(
        "Оберіть наступну дію:",
        reply_markup=admin_keyboard()
    )

@admin_router.message(StateFilter(AdminStates.waiting_for_command), F.text == "➕ Додати фільм/серіал")
async def process_add_media(message: types.Message, state: FSMContext):
    """Обробник додавання фільму/серіалу"""
    await message.answer(
        "Оберіть тип медіа:",
        reply_markup=media_type_keyboard()
    )

@admin_router.callback_query(lambda c: c.data.startswith("add_media_"))
async def callback_add_media_type(callback_query: types.CallbackQuery, state: FSMContext):
    """Обробник вибору типу медіа"""
    await callback_query.answer()
    
    # Отримуємо тип медіа з callback_data
    media_type = callback_query.data.split("_")[-1]
    
    # Зберігаємо тип медіа в стані
    await state.update_data(media_type=media_type)
    
    await state.set_state(AdminStates.waiting_for_media_title)
    await callback_query.message.edit_text("Введіть назву фільму/серіалу:")

@admin_router.callback_query(lambda c: c.data == "cancel_add_media")
async def callback_cancel_add_media(callback_query: types.CallbackQuery, state: FSMContext):
    """Обробник скасування додавання медіа"""
    await callback_query.answer()
    await state.set_state(AdminStates.waiting_for_command)
    await callback_query.message.edit_text(
        "Додавання медіа скасовано. Оберіть наступну дію:",
        reply_markup=None
    )
    await callback_query.message.answer(
        "Оберіть дію:",
        reply_markup=admin_keyboard()
    )

@admin_router.message(StateFilter(AdminStates.waiting_for_media_title))
async def process_media_title(message: types.Message, state: FSMContext):
    """Обробник введення назви медіа"""
    title = message.text.strip()
    
    if not title:
        await message.answer("Будь ласка, введіть коректну назву.")
        return
    
    # Зберігаємо назву в стані
    await state.update_data(media_title=title)
    
    await state.set_state(AdminStates.waiting_for_media_description)
    await message.answer("Введіть опис фільму/серіалу:")

@admin_router.message(StateFilter(AdminStates.waiting_for_media_description))
async def process_media_description(message: types.Message, state: FSMContext):
    """Обробник введення опису медіа"""
    description = message.text.strip()
    
    if not description:
        await message.answer("Будь ласка, введіть коректний опис.")
        return
    
    # Зберігаємо опис в стані
    await state.update_data(media_description=description)
    
    await state.set_state(AdminStates.waiting_for_media_poster)
    await message.answer("Введіть URL постера (або натисніть /skip для пропуску):")

@admin_router.message(StateFilter(AdminStates.waiting_for_media_poster))
async def process_media_poster(message: types.Message, state: FSMContext):
    """Обробник введення URL постера"""
    poster_url = message.text.strip()
    
    if message.text == "/skip":
        poster_url = ""
    
    # Зберігаємо URL постера в стані
    await state.update_data(media_poster=poster_url)
    
    # Отримуємо жанри
    data = await state.get_data()
    media_type = data.get("media_type")
    
    # Визначаємо ID категорії за типом медіа
    category_id = 1  # За замовчуванням - фільми
    
    if media_type == "tv":
        category_id = 2
    elif media_type == "animation":
        category_id = 3
    
    genres = db.get_genres(category_id)
    
    if not genres:
        await message.answer("Для обраної категорії немає жанрів. Додайте жанр перед додаванням медіа.")
        await state.set_state(AdminStates.waiting_for_command)
        await message.answer(
            "Оберіть дію:",
            reply_markup=admin_keyboard()
        )
        return
    
    # Формуємо текст з жанрами
    text = "Оберіть жанр для медіа (введіть номер):\n\n"
    for i, genre in enumerate(genres, 1):
        text += f"{i}. {genre['name']}\n"
    
    await state.set_state(AdminStates.waiting_for_media_genre)
    await message.answer(text)

@admin_router.message(StateFilter(AdminStates.waiting_for_media_genre))
async def process_media_genre(message: types.Message, state: FSMContext):
    """Обробник вибору жанру для медіа"""
    try:
        genre_index = int(message.text.strip()) - 1
    except ValueError:
        await message.answer("Будь ласка, введіть коректний номер жанру.")
        return
    
    # Отримуємо дані зі стану
    data = await state.get_data()
    media_type = data.get("media_type")
    
    # Визначаємо ID категорії за типом медіа
    category_id = 1  # За замовчуванням - фільми
    
    if media_type == "tv":
        category_id = 2
    elif media_type == "animation":
        category_id = 3
    
    genres = db.get_genres(category_id)
    
    if not genres or genre_index < 0 or genre_index >= len(genres):
        await message.answer("Жанр з таким номером не знайдений.")
        return
    
    genre_id = genres[genre_index]["id"]
    
    # Отримуємо всі дані зі стану
    title = data.get("media_title")
    description = data.get("media_description")
    poster_url = data.get("media_poster")
    
    # Додаємо медіа до бази даних
    db.add_custom_media(
        title=title,
        description=description,
        poster_url=poster_url,
        genre_ids=[genre_id],
        media_type=media_type,
        added_by=message.from_user.id
    )
    
    await message.answer(f"Медіа '{title}' успішно додано.")
    
    # Повертаємось до адмін-меню
    await state.set_state(AdminStates.waiting_for_command)
    await message.answer(
        "Оберіть наступну дію:",
        reply_markup=admin_keyboard()
    )

@admin_router.message(StateFilter(AdminStates.waiting_for_command), F.text == "🔙 Назад до меню")
async def process_back_to_menu_from_admin(message: types.Message, state: FSMContext):
    """Обробник кнопки повернення до головного меню з адмін-панелі"""
    await state.clear()
    await message.answer("Повертаємось до головного меню", reply_markup=main_menu_keyboard())

def register_admin_handlers(dp):
    """Реєстрація обробників для адміністративних функцій"""
    dp.include_router(admin_router) 