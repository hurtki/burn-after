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
            # если нет получаем все записи в базе данных с нужными параметрами
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
        
        
        if "-" in params.sort:
            posts_ids = cache.zrange(zset_key, params-1, params*settings.POSTS_PER_PAGE)
        