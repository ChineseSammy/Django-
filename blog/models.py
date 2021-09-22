# coding:utf-8

from django.db import models
from django.contrib import admin
from django.urls import reverse
from django.utils.timezone import now


# =============================用户========================================
class User(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=200)
    nickname = models.CharField(max_length=50, default='一颗小树苗')
    email = models.EmailField()
    created_time = models.CharField(max_length=50, default=now)
    # 评论数
    comment_num = models.PositiveIntegerField(default=0, verbose_name='评论数')
    # 头像
    avatar = models.ImageField(upload_to='media', default='media/default.png')

    def __str__(self):
        return self.username

    # 增加评论数
    def comment(self):
        self.comment_num += 1
        self.save(update_fields=['comment_num'])

    # 删除评论数
    def comment_del(self):
        self.comment_num -= 1
        self.save(update_fields=['comment_num'])

    class Meta:
        # 数据库表名
        db_table = 'blog_user'
        # 后台显示模型名
        verbose_name = '用户'
        verbose_name_plural = '用户'


# =============================文章评论========================================
class ArticleComment(models.Model):
    body = models.TextField()
    username = models.CharField(max_length=50)
    userimg = models.CharField(max_length=70)
    nickname = models.CharField(max_length=50, default='一颗小树苗')
    created_time = models.DateTimeField(default=now, verbose_name='创建时间')
    article = models.CharField(max_length=50)
    title = models.CharField(max_length=50)

    # 友好化对象后台显示
    def __str__(self):
        return self.article

    class Meta:
        # 排序
        ordering = ['-created_time']
        # 后台模型显示名称
        verbose_name = '评论'
        verbose_name_plural = '评论列表'
        # 数据库名
        db_table = 'comment'

    list_display = (article, body)


# =============================博客文章标签========================================
class Tags(models.Model):
    name = models.CharField(verbose_name='标签名', max_length=64)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        db_table = 'tag'
        verbose_name = '标签名称'
        verbose_name_plural = '标签列表'


# =============================博客文章分类========================================
class Category(models.Model):
    name = models.CharField(verbose_name='类别名称', max_length=64)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        db_table = 'category'
        verbose_name = '类别名称'
        verbose_name_plural = '分类列表'


# =============================博客文章========================================
class Article(models.Model):
    STATUS_CHOICES = (
        ('d', '草稿'),
        ('p', '发表'),
    )

    article_id = models.CharField(max_length=100, verbose_name='标号')
    title = models.CharField(max_length=100, verbose_name='标题')
    content = models.TextField(verbose_name='正文', blank=True, null=True)
    status = models.CharField(verbose_name='状态', max_length=1, choices=STATUS_CHOICES, default='p')
    views = models.PositiveIntegerField(default=0, verbose_name='浏览量')
    created_time = models.DateTimeField(verbose_name='创建时间', default=now)

    category = models.ForeignKey(
        Category, verbose_name='分类',
        on_delete=models.CASCADE,
        blank=False, null=False
                                 )
    tags = models.ManyToManyField(Tags, verbose_name='标签', blank=True)

    def __str__(self):
        return self.title

    # 更新浏览量
    def viewed(self):
        self.views += 1
        self.save(update_fields=['views'])

    # 上一篇
    def prev_article(self):
        # id比当前id小，状态为发表，发布时间不能为空
        return Article.objects.filter(id__lt=self.id, status='p', pub_time__isnull=False).first()

    # 下一篇
    def next_article(self):
        return Article.objects.filter(id__gt=self.id, status='p', pub_time__isnull=False).first()

    class Meta:
        ordering = ['-created_time']
        db_table = 'article'
        verbose_name = '文章'
        verbose_name_plural = '文章列表'
        get_latest_by = 'created_time'
