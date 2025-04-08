from django.urls import path
from . import views

urlpatterns = [
    # api для получения постов на главной странице 
    path('', views.PostsAPIView.as_view()),
    
]
