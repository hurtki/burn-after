# redis.py
from .models import Category, Post
from django.conf import settings
from .serializers import PostSerializer
from .redis_helper import cache, cache_set_json, cache_get_json, cache_delete, get_zset_length
from django.db.models import Count

# Функция для получения списка категорий из кеша
def get_categories_from_cache():
    categories = cache_get_json('categories_list')
    if not categories:
        categories = list(Category.objects.values_list('name', flat=True))
        cache_set_json('categories_list', categories, ex=settings.CATEGORIES_LIST_CACHE_SECONDS)
    return categories


# Функция для занесения категории в кеш
def add_category_to_cache(new_category_name):
    categories = get_categories_from_cache()
    if new_category_name not in categories:
        categories.append(new_category_name)
        cache_set_json('categories_list', categories, ex=settings.CATEGORIES_LIST_CACHE_SECONDS)


# Функция для получения сериализованного поста из кеша
def get_serialized_post_data_from_cache(ids):
    # создаем дикт для хранения сериализованных данных постов
    cached_data = {}
    # лист для хранения айдишников, которые мы не найдем в кеше
    missing_ids = []

    # проверяем каждый ключ в кеше
    for post_id in ids:
        data = cache_get_json(f'post:{post_id}')
        if data is not None:
            cached_data[post_id] = data
        else:
            missing_ids.append(post_id)

    # если есть айдишники, которых не было в кеше
    if missing_ids:
        # получаем только их из базы данных
        objects = Post.objects.filter(id__in=missing_ids)
        for obj in objects:
            serialized_data = PostSerializer(obj).data
            cache_set_json(f'post:{obj.id}', serialized_data, ex=settings.POST_CACHE_SECONDS)
            cached_data[obj.id] = serialized_data

    # собираем результат
    result = [cached_data[obj_id] for obj_id in ids]
    
    return result


# Получаем посты из Zset
def get_posts_for_page(zset_key, start, end, sort):
    if "-" in sort:
        return cache.zrevrange(zset_key, start, end)
    else:
        return cache.zrange(zset_key, start, end)


# Проверяем, есть ли список постов в кеше, если нет — добавляем его
def ensure_zset_cached(zset_key: str, category: Category, sort: str, is_exploded: bool) -> None:
    if not cache.zcard(zset_key):
        posts = Post.objects.filter(category=category, is_exploded=is_exploded).annotate(like_count=Count('likes'))

        for post in posts:
            score = post.created_at.timestamp() if sort == "created_at" else post.like_count
            cache.zadd(zset_key, {str(post.id): score})
            serialized_post = PostSerializer(post).data
            cache_set_json(f'post:{post.id}', serialized_post, ex=settings.POST_CACHE_SECONDS)


def get_length_of_zset(zset_key: str) -> int:
    return get_zset_length(zset_key)
