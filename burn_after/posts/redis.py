# сборник функций для работы с кешем 

from django.core.cache import cache
from .models import Category
from django.conf import settings

# функция для получения списка категорий из кеша
def get_categories_from_cache():
    categories = cache.get('categories_list')
    if not categories:
        categories = list(Category.objects.values_list('name', flat=True))
        cache.set('categories_list', categories, timeout=settings.CATEGORIES_LIST_CACHE_SECONDS)  
    return categories
# функция для занесения категории в кеш
def add_category_to_cache(new_category_name):
    categories = get_categories_from_cache()
    if new_category_name not in categories:
        categories.append(new_category_name)
        cache.set('categories_list', categories, timeout=settings.CATEGORIES_LIST_CACHE_SECONDS)
