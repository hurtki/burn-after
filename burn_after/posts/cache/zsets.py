from ..models import Category, Post
from burn_after.core import redis_helper as cache
from django.conf import settings
from django.db.models import Count
from ..serializers import PostSerializer


# Получаем посты из Zset
def get_posts_for_page(zset_key, start, end, sort) -> list:
    if "-" in sort:
        return cache.get_zset_segment(zset_key, start, end, True)
    else:
        return cache.get_zset_segment(zset_key, start, end, False)
    
# Проверяем, есть ли список постов в кеше, если нет — добавляем его
def ensure_zset_cached(zset_key: str, category: Category, sort_zset_key: str, is_exploded: bool) -> None:
    
    
    if not cache.exists(zset_key):
        posts = Post.objects.filter(category=category, is_exploded=is_exploded).annotate(like_count=Count('likes'))
        
        # словарь который будет отадвать нужный score по типу сортировки 
        sort_key_map = {
        "created_at": lambda post: post.created_at.timestamp(),
        "likes": lambda post: post.like_count,
        }
        
        
        
        for post in posts:
            # Защита от неожиданных значений sort, даже несмотря на предварительную валидацию
            assert sort_zset_key in sort_key_map, f"Unexpected sort key: {sort_zset_key}"
            
            score = sort_key_map[sort_zset_key](post)
            cache.set_zset(zset_key, {str(post.id): score})
            serialized_post = PostSerializer(post).data
            cache.set_json(f'post:{post.id}', serialized_post, ex=settings.POST_CACHE_SECONDS)

def get_length_of_zset(zset_key: str) -> int:
    return cache.get_zset_length(zset_key)

