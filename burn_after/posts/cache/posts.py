from burn_after.core import redis_helper as cache
from ..models import Post
from django.conf import settings

from ..serializers import PostSerializer


def get_serialized_post_data_from_cache(ids: list) -> list:
    """Функция для получения сериализованных постов по списку айдишников"""
    # создаем дикт для хранения сериализованных данных постов
    cached_data = {}
    # лист для хранения айдишников, которые мы не найдем в кеше
    missing_ids = []
    # проверяем каждый ключ в кеше
    for post_id in ids:
        data = cache.get_json(f'post:{post_id}')
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
            cache.set_json(f'post:{obj.id}', serialized_data, ex=settings.POST_CACHE_SECONDS)
            # тк списой айдишников в строках то и айдишник объекта из базы тоже в строку чтобы потом не ломалось при их переборе 
            cached_data[str(obj.id)] = serialized_data

    # собираем результат
    result = [cached_data[obj_id] for obj_id in ids]
    
    return result