from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    # поле название категории 
    name = models.CharField("name", max_length=12)
    # автор категории 
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
# модель поста 
class Post(models.Model):
    # поле внешнего ключа пользователя который опубликовал пост 
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    # поле заголовка
    title = models.CharField("title", max_length=25)
    # основной текст поста
    content = models.TextField("Content", max_length=900)
    # четкое время создания поста 
    created_at = models.DateTimeField("time of creation", auto_now_add=True)
    # система лайков 
    likes = models.ManyToManyField(User, through='Like', related_name='liked_posts')
    # категория поста 
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    # взорванный пост или нет 
    is_exploded = models.BooleanField("is_exploded")
    
    def __str__(self):
        return f"post: {self.title}"
    
# модель связи поста и пользователя ( модель лайка )
class Like(models.Model):
    # пользователь 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # пост которому лайк
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    # дата создания поста
    created_at = models.DateTimeField("time of creation", auto_now_add=True)
    
    
    
    class Meta:
        # объявляем что у пользователя и поста может быть только одна связь 
        unique_together = ('user', 'post')
        
    def __str__(self):
        return f'{self.user.username} liked {self.post.title}'