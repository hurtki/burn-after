from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import PostQueryParamsSerializer, PostSerializer
from .models import Post, Category
from django.conf import settings
import json
from datetime import datetime
from django.db.models import Count
from .redis import get_serialized_post_data_from_cache, get_posts_for_page, ensure_zset_cached, get_length_of_zset
import redis


class PostsAPIView(APIView):
    # создаем метод для получения списка постов по трем параметрам 
    def get(self, request):
        
        # превращаем параметры в дикт со значением не листом 
        # в будущем для например поиска по двум категориям можно будет менять 
        data = {}
        for k, v in request.query_params.lists():
            if isinstance(v, list):
                data[k] = v[0]
            else:
                data[k] = v
        
        # сериализируем querrys параметры для хорошей валидации ( смотри serializers.py )
        serializer = PostQueryParamsSerializer(data=data)
        
        # проверяем на валидность сериализированные данные и отправляем ошибку если не валидны 
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        # получаем три валидрованных querry параметра из сериализатора 
        category = serializer.validated_data["category"]
        sort = serializer.validated_data["sort"]
        is_exploded = serializer.validated_data["is_exploded"]
        page = serializer.validated_data["page"]
        
        # поулчаем ОБЪЕКТ категории из базы данных
        # в будущем надо хранить его в кеше для того чтобы вообще не обращаться к бд 
        category = Category.objects.filter(name=category).first()
        
        # формируем ключ по которому должен находится zset в кеше с отсортированным множеством четкой категории 
        zset_key = f"category:{category}:{sort}:{is_exploded}"
        # запускаем функцию для проверки наличия ZSET в кеше, если его там не будет она обратиться к базе данных и добавит его 
        ensure_zset_cached(category=category, sort=sort, is_exploded=is_exploded, zset_key=zset_key)
        

        # находим точки пагирования по которым будем обрезать 
        start = (page - 1) * settings.POSTS_PER_PAGE
        end = page * settings.POSTS_PER_PAGE

        # смотрим общее кол-во айдишников для проверки наличия постов на запрашиваемой странице 

        total_posts = get_length_of_zset(zset_key=zset_key)

        # если нету ни одного поста то возвращаем ошибку об отсутствии страницы 
        if start >= total_posts:
            return Response({
                "page_error": "not enough items"
            }, status=400)
        # смотри было ли в запросе отрицание сортировки и в зависимости от этого вытаскиваем айдишники из кеша
        posts_ids = get_posts_for_page(zset_key, start, end, sort)
        return Response(get_serialized_post_data_from_cache(posts_ids))