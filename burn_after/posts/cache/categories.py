from ..models import Category
from burn_after.core import redis_helper as cache
from django.conf import settings

# Функция для получения списка категорий из кеша или их замены в кеше на данные из базы данных
def get_categories_from_cache() -> list:
    categories = cache.get_json('categories_list')
    if not categories:
        categories = list(Category.objects.values_list('name', flat=True))
        cache.set_json('categories_list', categories, ex=settings.CATEGORIES_LIST_CACHE_SECONDS)
    return categories

# Функция для занесения категории в кеш
def add_category_to_cache(new_category_name) -> None:
    categories = get_categories_from_cache()
    if new_category_name not in categories:
        categories.append(new_category_name)
        cache.set_json('categories_list', categories, ex=settings.CATEGORIES_LIST_CACHE_SECOND)