# coding:utf-8

from PIL import Image
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse, Http404
from django.shortcuts import render

from Samblog import settings
from blog.models import User, ArticleComment, Article, Tags, Category


def index_unlog(request):
    return render(request, 'index_unlog.html')


def login(request):
    if request.method == 'POST':
        username=request.POST.get('username')
        password=request.POST.get('password')

        # 检测用户是否存在数据库中
        user = User.objects.filter(username=username)
        # 如果存在
        if user:
            # 读取该用户的信息
            user = User.objects.get(username=username)
            # 检测密码
            if password == user.password:
                request.session['IS_LOGIN'] = True
                request.session['nickname'] = user.nickname
                request.session['username'] = username
                avatar = 'media/' + username + '.png'
                request.session['avatar'] = avatar
                return render(request, 'index.html', {'user': user})
            else:
                return render(request, 'login.html', {'error': '密码错误'})

    return render(request, 'login.html')


def register(request):
    if request.method == 'POST':
        username=request.POST.get('username')
        password1=request.POST.get('password1')
        password2=request.POST.get('password2')
        nickname=request.POST.get('nickname')
        email=request.POST.get('email')
        avatar=request.FILES.get('avatar')

        if User.objects.filter(username=username):
            return render(request, 'register.html', {'error': '用户已存在'})
        if password1 != password2:
            return render(request, 'register.html', {'error': '两次输入密码不一致'})

        user = User()

        if avatar:
            user.avatar = 'media/' + username + '.png'
            img = Image.open(avatar)
            size = img.size
            print(size)
            # 因为需要圆形，所以需要获取正方形图片
            r2 = min(size[0], size[1])
            if size[0] != size[1]:
                img = img.resize((r2, r2), Image.ANTIALIAS)
            # 生成圆的r
            r3 = int(r2/2)
            img_circle = Image.new('RGBA', (r3*2, r3*2), (255,255,255,0))
            # 像素的访问对象
            pima = img.load()
            pimb = img_circle.load()
            # 圆心横坐标
            r = float(r2/2)

            for i in range(r2):
                for j in range(r2):
                    # 到圆心距离的横坐标
                    lx = abs(i-r)
                    # 到圆心距离的纵坐标
                    ly = abs(j-r)
                    # 三角函数
                    l = (pow(lx, 2) + pow(ly, 2))**0.5

                    if l < r3:
                        pimb[i-(r-r3), j-(r-r3)] = pima[i, j]
            img_circle.save('blog/static/media/' + username + '.png')
        user.username = username
        user.password = password1
        user.email = email
        user.nickname = nickname
        user.save()
        # 返回注册成功页面
        return render(request, 'index_unlog.html')
    else:
        return render(request, 'register.html')


def home(request):
    is_login = request.session.get('IS_LOGIN', False)
    if is_login:
        posts = Article.objects.all()  # 获取全部的Article对象
        paginator = Paginator(posts, settings.PAGE_NUM)  # 每页显示数量，对应settings.py中的PAGE_NUM
        page = request.GET.get('page')  # 获取URL中page参数的值
        try:
            post_list = paginator.page(page)
        except PageNotAnInteger:
            post_list = paginator.page(1)
        except EmptyPage:
            post_list = paginator.page(paginator.num_pages)
        nickname = request.session['nickname']
        username = request.session['username']
        avatar = request.session['avatar']
        return render(request, 'home.html', {'post_list': post_list, 'nickname': nickname, 'avatar': avatar})
    return render(request, 'index_unlog.html')


def log_out(request):
    del request.session['IS_LOGIN']
    del request.session['username']
    del request.session['nickname']
    return render(request, 'index_unlog.html')


def forget(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        email = request.POST.get('email', '')
        user = User.objects.filter(username=username)
        if user:
            user = User.objects.get(username=username)
            if user.email != email:
                return render(request, 'forget.html', {'error': '邮箱不正确'})
            request.session['username'] = username
            return render(request, 'reset.html')
        else:
            return render(request, 'forget.html', {'error': '请输入正确的用户名'})
    else:
        return render(request, 'forget.html')

def reset(request):
    if request.method == 'POST':
        password1 = request.POST.get('password1','')
        password2 = request.POST.get('password2','')
        username = request.session['username']
        user = User.objects.get(username=username)
        if password1 == password2:
            user.password = password1
            user.save()
            return render(request, 'login.html')
        else:
            return render(request, 'reset.html', {'error': '两次密码输入不一致！'})
    else:
        return render(request, 'reset.html')


def tags(request):
    nickname = request.session['nickname']
    tags = Tags.objects.all()
    paginator = Paginator(tags, settings.TAG_NUM)  # 每页显示数量，对应settings.py中的PAGE_NUM
    page = request.GET.get('page')  # 获取URL中page参数的值

    try:
        tags = paginator.page(page)
    except PageNotAnInteger:
        tags = paginator.page(1)
    except EmptyPage:
        tags = paginator.page(paginator.num_pages)
    return render(request,'tags.html', {'tag_list': tags,'nickname':nickname,'avatar':request.session['avatar']})


def userinfo(request):
    username = request.session['username']
    user = User.objects.get(username=username)
    comments = ArticleComment.objects.filter(username=username)

    paginator = Paginator(comments, settings.COMMENT_NUM)  # 每页显示数量，对应settings.py中的PAGE_NUM
    page = request.GET.get('page')  # 获取URL中page参数的值
    avatar = 'media/' + username + '.png'

    try:
        comment_list = paginator.page(page)
    except PageNotAnInteger:
        comment_list = paginator.page(1)
    except EmptyPage:
        comment_list = paginator.page(paginator.num_pages)
    return render(request,'user_info.html',{'user':user,'comment_list':comment_list,'avatar':avatar})


def search(request):
    if request == 'POST':
        searchinfo = request.POST.get('info', '')
        posts = Article.objects.filter(title__icontains=searchinfo)

        paginator = Paginator(posts, settings.PAGE_NUM)  # 每页显示数量，对应settings.py中的PAGE_NUM
        page = request.GET.get('page')  # 获取URL中page参数的值

        try:
            post_list = paginator.page(page)
        except PageNotAnInteger:
            post_list = paginator.page(1)
        except EmptyPage:
            post_list = paginator.page(paginator.num_pages)
        return render(request, 'search.html', {'post_list': post_list, 'nickname': request.session['nickname'],
                                               'avatar': request.session['avatar']})
    return render(request, 'home.html')


def tags_detail(request, id):
    posts =Article.objects.filter(tags = id)
    tag = Tags.objects.get(id = id)
    paginator = Paginator(posts, settings.PAGE_NUM)  # 每页显示数量，对应settings.py中的PAGE_NUM
    page = request.GET.get('page')  # 获取URL中page参数的值
    try:
        post_list = paginator.page(page)
    except PageNotAnInteger:
        post_list = paginator.page(1)
    except EmptyPage:
        post_list = paginator.page(paginator.num_pages)
    return render(request, 'tags_detail.html', {'post_list': post_list,'tag':tag,'nickname': request.session['nickname'],'avatar':request.session['avatar']})


def category(request,id):
    nickname = request.session['nickname']
    posts =Article.objects.filter(category_id = str(id))
    paginator = Paginator(posts, settings.PAGE_NUM)  # 每页显示数量，对应settings.py中的PAGE_NUM
    page = request.GET.get('page')  # 获取URL中page参数的值
    try:
        post_list = paginator.page(page)
    except PageNotAnInteger:
        post_list = paginator.page(1)
    except EmptyPage:
        post_list = paginator.page(paginator.num_pages)
    return render(request, 'category.html', {'post_list': post_list,'nickname': nickname,'avatar':request.session['avatar']})


def detail(request, id):  # 查看文章详情
    try:
        post = Article.objects.get(article_id=str(id))
        post.viewed()   # 更新浏览次数
        tags = post.tags.all()  # 获取文章对应所有标签
    except Article.DoesNotExist:
        raise Http404
    comments = ArticleComment.objects.filter(article = str(id))
    paginator = Paginator(comments, 3)  # 每页显示3条评论
    page = request.GET.get('page')  # 获取URL中page参数的值
    try:
        comment_list = paginator.page(page)
    except PageNotAnInteger:
        comment_list = paginator.page(1)
    except EmptyPage:
        comment_list = paginator.page(paginator.num_pages)
    previous_post = Article.objects.filter(article_id=str(id-1))
    if previous_post and id!=0:
        previous_post = Article.objects.get(article_id=str(id-1))
    next_post = Article.objects.filter(article_id=str(id+1))
    if next_post:
        next_post = Article.objects.get(article_id=str(id+1))
    return render(request, 'post.html', {'post': post, 'nickname':request.session['nickname'],
                                         'tags': tags,'comment_list':comment_list,'previouspost':previous_post,'nextpost':next_post,'avatar':request.session['avatar']})

def commentpost(request):
    if request.method == 'POST':
        comment = request.POST.get('comment','')
        id = request.POST.get('id')
        print("ok")
        if comment!='':
            message = comment
            user_img = 'media/'+request.session['username']+'.png'
            nick_name = request.session['nickname']
            user_name = request.session['username']
            article = Article.objects.get(article_id = str(id))
            newrecord = ArticleComment()
            #newrecord.username = user_name
            newrecord.body = message
            newrecord.article = id
            newrecord.userimg = user_img
            newrecord.username = user_name
            newrecord.nickname = nick_name
            newrecord.title = article.title
            newrecord.save()
            user = User.objects.get(username = user_name)
            user.comment()
            return HttpResponse()


def comment_del(request):
    if request.method == 'POST':
        comment_id = request.POST.get('comment_id')
        username = request.session['username']
        user = User.objects.get(username=username)
        ArticleComment.objects.filter(id=str(comment_id)).delete()

        user.comment_del()
        comments = ArticleComment.objects.filter(username=username)
        paginator = Paginator(comments, 1)  # 每页显示数量，对应settings.py中的PAGE_NUM
        page = request.GET.get('page')  # 获取URL中page参数的值
        try:
            comment_list = paginator.page(page)
        except PageNotAnInteger:
            comment_list = paginator.page(1)
        except EmptyPage:
            comment_list = paginator.page(paginator.num_pages)
        return HttpResponse()