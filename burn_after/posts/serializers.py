from rest_framework import serializers
from .models import Post
# from .redis import get_categories_from_cache

class PostQueryParamsSerializer(serializers.Serializer):
    category = serializers.CharField(required=True, allow_blank=False)
    sort = serializers.CharField(required=True, allow_blank=False) # created_at / -created_at / likes_count / -likes_count
    page = serializers.IntegerField(required=True, min_value=1)
    is_exploded = serializers.BooleanField(required=True)

    # метод для валидации параметра сортировки 
    def validate_sort(self, value):
        # допустимые параметры сортировки 
        allowed_values = ['created_at', '-created_at', 'likes', '-likes']
        if value not in allowed_values:
            raise serializers.ValidationError(f'Invalid sort value. Allowed values are {", ".join(allowed_values)}.')
        return value

    def validate_category(self, value):
        from .redis import get_categories_from_cache
        category = value[0] if isinstance(value, list) else value
        if not category in get_categories_from_cache():
            raise serializers.ValidationError(f"Category with name{value} doesn't exist")
        return category
# сериализатор постов 
class PostSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'content',
            'created_at',
            'author_username',
            'category_name'
        ]
    