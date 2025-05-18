from aiogram.fsm.state import State, StatesGroup

class AdminStates(StatesGroup):
    """Стани для роботи з адміністративними функціями"""
    waiting_for_command = State()
    waiting_for_category_name = State()
    waiting_for_category_description = State()
    waiting_for_genre_name = State()
    waiting_for_genre_api_id = State()
    waiting_for_genre_category = State()
    waiting_for_media_title = State()
    waiting_for_media_description = State()
    waiting_for_media_poster = State()
    waiting_for_media_genre = State()

class SearchStates(StatesGroup):
    """Стани для пошуку"""
    waiting_for_query = State() 