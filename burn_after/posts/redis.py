# сборник функций для работы с кешем 

from django.core.cache import cache
from .models import Category, Post
from django.conf import settings
from .serializers import PostSerializer

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


def get_serialized_post_data_from_cache(ids):
    # создаем дикт для хранения сериализированных данных постов 
    cached_data = {}
    # лист для хранения айдишников которые мы не найдем в кеше 
    missing_ids = []

    # проверяем каждый ключ в кеше 
    for post_id in ids:
        data = cache.get(f'post:{post_id}')
        # если есть данные то сохраняем в дикт если нету то в лист
        if data is not None:
            cached_data[post_id] = data
        else:
            missing_ids.append(post_id)

    # теперь если есть айди которых не было  
    if missing_ids:
        # получаем только их из базы данных 
        objects = Post.objects.filter(id__in=missing_ids)
        # перебираем полученные объекты
        for obj in objects:
            # сериализируем каждого из них 
            serialized_data = PostSerializer(obj).data
            # записываем сериализированный пост в кеш
            cache.set(f'post:{obj.id}', serialized_data)
            # добавляем сериализированные данные в возвращаемый дикт
            cached_data[obj.id] = serialized_data

    # собираем 
    result = [cached_data[obj_id] for obj_id in ids]
    
    return result

def get_posts_for_page(zset_key, start, end, sort):
    if "-" in sort:
        return cache.zrevrange(zset_key, start, end)
    else:
        return cache.zrange(zset_key, start, end)