from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from posts.models import Category, Post, Like
from faker import Faker
import random

class Command(BaseCommand):
    help = "Seed the database with sample users, categories, posts, and likes"

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Создаём или берём пользователя
        user, created = User.objects.get_or_create(username="testuser")
        if created:
            user.set_password("1234")
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Создан пользователь: {user.username}"))
        else:
            self.stdout.write(f"Пользователь {user.username} уже существует")

        # Создаём категории
        categories = []
        for _ in range(3):
            category = Category.objects.create(
                name=fake.word()[:12],
                author=user
            )
            categories.append(category)

        self.stdout.write(f"Создано {len(categories)} категорий")

        # Создаём посты
        posts = []
        for _ in range(5):
            post = Post.objects.create(
                author=user,
                title=fake.sentence(nb_words=4)[:25],
                content=fake.text(max_nb_chars=300),
                category=random.choice(categories),
                is_exploded=random.choice([True, False])
            )
            posts.append(post)

        self.stdout.write(f"Создано {len(posts)} постов")

        # Добавляем лайки
        for post in posts:
            if random.choice([True, False]):
                Like.objects.get_or_create(user=user, post=post)

        self.stdout.write(self.style.SUCCESS("✅ База успешно наполнена фейковыми данными!"))
