# coding:utf-8

from django.contrib import admin
from blog.models import Article, Category, Tags, User, ArticleComment
from django_summernote.admin import SummernoteModelAdmin


class PostAdmin(SummernoteModelAdmin):
    summernote_fields = ('content')  # 给后台content字段添加富文本
    list_display = ['article_id', 'title', 'created_time']
    search_fields = ['title']  # 搜索框
    list_filter = ['created_time']  # 过滤器


class CommentAdmin(admin.ModelAdmin):
    list_display = ['username', 'body', 'title']
    search_fields = ['title']  # 搜索框


admin.site.register(Tags)
admin.site.register(User)
admin.site.register(Category)
admin.site.register(ArticleComment, CommentAdmin)
admin.site.register(Article, PostAdmin)
