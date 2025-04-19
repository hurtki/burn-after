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


def set_json(key, value: dict, ex=None):
    """Сериализует значение и сохраняет в кеш."""
    cache.set(key, json.dumps(value), ex=ex)

def get_json(key):
    """Читает значение из кеша и десериализует его."""
    data = cache.get(key)
    return json.loads(data) if data else None


def delete(key):
    """Удаляет ключ из кеша."""
    cache.delete(key)


def get_zset_length(zset_key):
    """Возвращает длину Zset в Redis."""
    return cache.zcard(zset_key)

def get_zset_segment(zset_key, start: int, end: int, sort_reflection: bool) -> list:
    """Возвращает отрезок элемнтов по старту и концу из zset"""
    if sort_reflection:
        return cache.zrevrange(zset_key, start, end)
    else:
        return cache.zrange(zset_key, start, end)
        
def exists(key) -> bool:
    """проверяет наличие ключа в кеше"""
    return cache.exists(key)

def set_zset(zset_key, mapping: dict):
    """создает zset по ключу с нужной разметкой"""
    cache.zadd(zset_key, mapping=mapping)

