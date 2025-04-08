from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import PostQueryParamsSerializer, PostSerializer
from django.core.cache import cache
from .models import Post
from django.conf import settings
import json
from datetime import datetime
from django.db.models import Count
from .redis import get_serialized_post_data_from_cache, get_posts_for_page



class PostsAPIView(APIView):
    # создаем метод для получения списка постов по трем параметрам 
    def get(self, request):
        # сериализируем querrys параметры для хорошей валидации ( смотри serializers.py )
        serializer = PostQueryParamsSerializer(data=request.query_params)
        # проверяем на валидность сериализированные данные и отправляем ошибку если не валидны 
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        # получаем три валидрованных querry параметра из сериализатора 
        params = serializer.validated_data
        # формируем ключ по которому должен находится zset в кеше с отсортированным множеством четкой категории 
        zset_key = f"category:{params.category}:{params.sort}:{params.is_exploded}"
        # проверяем есть нужнй нам ZSET в кеше 
        if not cache.get(zset_key):
            # если нет получаем все записи в базе данных с нужными параметрами + аннотируем поле с кол-вом лайков 
            posts = Post.objects.filter(category=params.category, is_exploded=params.is_exploded).annotate(like_count=Count('likes'))
            # объявляем по чему будет провдится сортировка 
            score = post.created_at.timestamp() if params.sort == "created_at" else post.like_count
            # добавляем каждый пост в нужный zset в кеше 
            for post in posts:
                # добавляем пр ключу объект в zset
                cache.zadd(zset_key, {post.id: score})  # Или другой score
                # сериализируем пост полученный до этого из базы данных 
                serialized_post = PostSerializer(post).data
                # а теперь присваваем по ключу айди поста - сериализированный пост, как json строку 
                cache.set(f'post:{post.id}', json.dumps(serialized_post), timeout=settings.POST_CACHE_SECONDS)
                

        # находим точки пагирования по которым будем обрезать 
        start = (params.page - 1) * settings.POSTS_PER_PAGE
        end = params.page * settings.POSTS_PER_PAGE

        # смотрим общее кол-во айдишников для проверки наличия постов на запрашиваемой странице 
        total_posts = cache.zcard(zset_key)

        # если нету ни одного поста то возвращаем ошибку об отсутствии страницы 
        if start >= total_posts:
            return Response({
                "page_error": "not enough items"
            }, status=400)
        # смотри было ли в запросе отрицание сортировки и в зависимости от этого вытаскиваем айдишники из кеша
        posts_ids = get_posts_for_page(zset_key, start, end, params.sort)
            
        return Response(get_serialized_post_data_from_cache(posts_ids))