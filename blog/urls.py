# coding:utf-8

from django.urls import path
from blog import views

app_name = 'blog'

urlpatterns = [
    path('home', views.home,name='home'),
    path('tags', views.tags, name='tags'),
    path('userinfo', views.userinfo, name='userinfo'),
    path('search', views.search, name='search'),
    path('tags/detail/<int:id>', views.tags_detail, name='tags_detail'),
    path('category/<int:id>', views.category, name='category'),
    path('articles/<int:id>/', views.detail, name='detail'),
    path('commentpost', views.commentpost, name='commentpost'),
    path('commentdel', views.comment_del, name='comment_del'),
]
