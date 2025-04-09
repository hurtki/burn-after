from django.contrib import admin

from .models import Category, Post, Like

admin.site.register(Category)
admin.site.register(Post)
admin.site.register(Like)
