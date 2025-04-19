from django.urls import path
from . import views

urlpatterns = [
    # api для получения постов на главной странице 
    path('', views.PostsAPIView.as_view()),
    # дальше будут апишки для какого-то взаимодействия с четким постом 
    # первая для смены состояния лайка, только для авторизированных пользователей 
    #  path('<int>/like', views.LikeAPIView.as_view())
]
