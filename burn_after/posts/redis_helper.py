# redis_helper.py
import json
from django.conf import settings
import redis

# создаем объект для взаимодействия с редисом
cache = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,  # дефолтный
    decode_responses=True  # чтобы строки возвращались как str, а не bytes
)

# Функция для сериализации и записи данных в кеш
def cache_set_json(key, value: dict, ex=None):
    """Сериализует значение и сохраняет в кеш."""
    cache.set(key, json.dumps(value), ex=ex)

# Функция для чтения данных из кеша и десериализации
def cache_get_json(key):
    """Читает значение из кеша и десериализует его."""
    data = cache.get(key)
    return json.loads(data) if data else None

# Функция для удаления данных из кеша
def cache_delete(key):
    """Удаляет ключ из кеша."""
    cache.delete(key)

# Функция для получения длины Zset
def get_zset_length(zset_key):
    """Возвращает длину Zset в Redis."""
    return cache.zcard(zset_key)
