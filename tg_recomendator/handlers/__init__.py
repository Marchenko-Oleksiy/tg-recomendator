from .common import register_common_handlers
from .admin import register_admin_handlers
from .categories import register_categories_handlers
from .search import register_search_handlers
from .trending import register_trending_handlers

def register_handlers(dp):
    register_common_handlers(dp)
    register_admin_handlers(dp)
    register_categories_handlers(dp)
    register_search_handlers(dp)
    register_trending_handlers(dp)