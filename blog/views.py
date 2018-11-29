from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, HttpResponse,redirect

# Create your views here.
# 用户认证模块
from django.contrib import auth
from django.http import JsonResponse
from blog.Myforms import UserForm
from blog.models import UserInfo
from blog import models
import json
from django.db.models import F
from django.db import transaction
from django.http import JsonResponse
from django.db.models import Avg, Max, Min, Sum, Count
from django.db import transaction
from django.contrib.auth.decorators import login_required


def login(request):
    if request.method == 'POST':
        response = {'user': None, 'msg': None}
        user = request.POST.get('user')
        pwd = request.POST.get('pwd')
        # 读取验证码
        valid_code = request.POST.get('valid_code')
        # 回话跟踪技术，保存验证码
        valid_code_str = request.session.get('valid_code_str')
        # 如果书写的验证码和生成的验证码一致
        # 不区分大小写---可以统一变成大写
        if valid_code.upper() == valid_code_str.upper():
            user = auth.authenticate(username=user, password=pwd)
            if user:
                auth.login(request, user)  # request.user==当前登录对象
                response['user'] = user.username
            else:
                response['msg'] = 'username or password error'
        else:
            response['msg'] = 'valid code error!'
        return JsonResponse(response)
    # ajax返回一个响应字符串
    return render(request, 'login.html')


# 随机验证码
def get_validCode_img(request):
    from blog.utils.validCode import get_valid_Code_img
    data = get_valid_Code_img(request)
    return HttpResponse(data)


def index(request):
    article_list=models.Article.objects.all()
    return render(request, 'index.html', locals())


# 注册
def register(request):
    # 实例化 form 对象

    if request.is_ajax():
        print(request.POST)
        # 对传来的数据进行验证
        form = UserForm(request.POST)
        response = {'user': None, 'msg': None}
        if form.is_valid():
            response['user'] = form.cleaned_data.get('user')
            # 注册成功要把数据添加进数据库
            # 生成一条用户记录
            user = form.cleaned_data.get('user')
            pwd = form.cleaned_data.get('pwd')
            email = form.cleaned_data.get('email')
            avatar_obj = request.FILES.get('avatar')
            # if avatar_obj:
            #     user_obj = UserInfo.objects.create_user(username=user, password=pwd, email=email, avatar=avatar_obj)
            # else:
            #     user_obj = UserInfo.objects.create_user(username=user, password=pwd, email=email)
            extra = {}
            if avatar_obj:
                extra["avatar"] = avatar_obj

            UserInfo.objects.create_user(username=user, password=pwd, email=email, **extra)


        else:
            print(form.cleaned_data)
            print(form.errors)
            response['msg'] = form.errors
            # 返回给Ajax
        return JsonResponse(response)
    form = UserForm()
    return render(request, 'register.html', locals())

# 注销
def logout(request):
    request.session.flush()
    auth.logout(request)
    return redirect('/login/')



def get_classification_data(username):
    user_obj = models.UserInfo.objects.filter(username=username).first()
    blog = user_obj.blog
    cate_list = models.Category.objects.filter(blog=blog).values('pk').annotate(c=Count('article__title')).values_list(
        'title', 'c')
    tag_list = models.Tag.objects.filter(blog=blog).values('pk').annotate(count=Count('article')).values_list('title',
                                                                                                              'count')
    date_list = models.Article.objects.filter(user=user_obj).extra(
        select={'y_m_date': "date_format(create_time,'%%Y-%%m')"}).values('y_m_date').annotate(
        c=Count('nid')).values_list('y_m_date', 'c')
    return {"blog": blog, "cate_list": cate_list, "date_list": date_list, "tag_list": tag_list}


def home_site(request,username,**kwargs):
    '''
    个人站点视图函数
    :param request:
    :return:
    '''
    user_obj=models.UserInfo.objects.filter(username=username).first()

    # 判断用户是否存在
    if not user_obj:
        return render(request,'not_found.html')
    blog = user_obj.blog
    print(blog)

    # 当前用户或者当前站点所对应文章

    # 方式一基于对象查询
    # 作者和文章的关系---> 一对多(文章)
    # article_list=user_obj.article_set.all()
    # 方式二 基于双下划线 __ 跨表查询
    article_list=models.Article.objects.filter(user=user_obj)
    # 判断是否跳转到其他地方
    # re_path("^(?P<username>\w+)/(?P<condition>tag|category|archive)/(?P<param>.*)/$", views.home_site),
    if kwargs:
        condition = kwargs.get("condition")  # 标签\分类\归档
        param = kwargs.get("param")  # 具体的哪一个
        if condition == "category":
            article_list = article_list.filter(category__title=param)
        elif condition == "tag":
            article_list = article_list.filter(tags__title=param)
            print(article_list)
        else:
            year, month = param.split('-')
            print(year, month)
            article_list = article_list.filter(create_time__year=year,create_time__month=month)
            print(article_list)



    # 查询每一个分类名称以及对应的文章数
    # annotate(聚合函数(关联表__统计字段)).values("表模型的所有字段以及统计字段")
    # values('group by的字段')
    # ret=models.Category.objects.values('pk').annotate(c=Count('article__title')).values('title','c')
    # print(ret)

    # 查询当前站点的每一个分类名称以及对应的文章数
    cate_list=models.Category.objects.filter(blog=blog).values('pk').annotate(c=Count('article__title')).values_list('title','c')
    print(cate_list)

    # 每一个标签以及对应得文章数
    tag_list=models.Tag.objects.filter(blog=blog).values('pk').annotate(count=Count('article')).values_list('title','count')
    print('tag_list',tag_list)

    # 单表分组查询
    # 查询当前站点每一个年月的名称以及对应的文章数
    # 方式一
    date_list = models.Article.objects.filter(user=user_obj).extra(
        select={'y_m_date': "date_format(create_time,'%%Y-%%m')"}).values('y_m_date').annotate(
        c=Count('nid')).values_list('y_m_date', 'c')
    print(date_list)

    # 方式二
    from django.db.models.functions import TruncMonth
    #
    # date_list=models.Article.objects.filter(user=user_obj).annotate(month=TruncMonth('create_time')).values('month').annotate(c=Count('nid')).values_list('month','c')
    # print(date_list)

    return render(request, "home_site.html", locals())


def article_detail(request,username,article_id):
    user_obj = models.UserInfo.objects.filter(username=username).first()
    blog = user_obj.blog
    cate_list = models.Category.objects.filter(blog=blog).values('pk').annotate(c=Count('article__title')).values_list(
        'title', 'c')
    tag_list = models.Tag.objects.filter(blog=blog).values('pk').annotate(count=Count('article')).values_list('title',
                                                                                                              'count')
    date_list = models.Article.objects.filter(user=user_obj).extra(
        select={'y_m_date': "date_format(create_time,'%%Y-%%m')"}).values('y_m_date').annotate(
        c=Count('nid')).values_list('y_m_date', 'c')

    article_obj = models.Article.objects.filter(pk=article_id).first()
    comment_list = models.Comment.objects.filter(article_id=article_id)
    return render(request, "article_detail.html", locals())
#     {'context':context,'blog':blog,'article_obj':article_obj,'comment_list':comment_list}


def digg(request):
    print(request.POST)
    article_id=request.POST.get('article_id')
    # is_up=request.POST.get('is_up') # 字符串
    is_up=json.loads(request.POST.get('is_up')) # 字符串
    # 点赞人即当前登录人
    user_id=request.user.pk

    # 重复点赞和反对--都无效
    obj=models.ArticleUpDown.objects.filter(user_id=user_id,article_id=article_id).first()
    response={'state':True,'msg':None}
    if not obj:
        ard=models.ArticleUpDown.objects.create(user_id=user_id,article_id=article_id,is_up=is_up)
        queryset= models.Article.objects.filter(pk=article_id)
        if is_up:
            queryset.update(up_count=F('up_count')+1)
        else:
            queryset.update(down_count=F('up_count')+1)

    else:
        response['state']=False
        response['handled']=obj.is_up
    return JsonResponse(response)

# 评论处 属于输入-也要防止xss
def comment(request):
    """
    提交评论视图函数
    功能:
    1 保存评论
    2 创建事务
    3 发送邮件
    :param request:
    :return:
    """
    print(request.POST)

    article_id = request.POST.get("article_id")
    pid = request.POST.get("pid")
    content = request.POST.get("content")
    user_id = request.user.pk
    article_obj=models.Article.objects.filter(pk=article_id).first()
    # 事务 from django.db import transaction
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(content, "html.parser")
    for tag in soup.find_all():
        if tag.name == "script":
            tag.decompose()

    with transaction.atomic():
        comment_obj=models.Comment.objects.create(user_id=user_id,article_id=article_id,content=str(soup),parent_comment_id=pid)
        # 数据同步 F比较两个字段
        models.Article.objects.filter(pk=article_id).update(comment_count=F('comment_count')+1)

    response={}
    response['create_time']=comment_obj.create_time.strftime("%Y-%m-%d %X")
    response['username']=request.user.username
    response['content']=str(soup)

    # 发邮件
    from django.core.mail import send_mail
    from cnblog import settings
    import threading
    t=threading.Thread(target=send_mail,args=('您的文章%s新增了一条内容' % article_obj.title,str(soup),
                                                 settings.EMAIL_HOST_USER,
                                                 ["836342406@qq.com"]))
    t.start()

    return JsonResponse(response)


def get_comment_tree(request):
    article_id=request.GET.get('article_id')
    ret=list(models.Comment.objects.filter(article_id=article_id).values('pk','content','parent_comment_id'))
    return JsonResponse(ret,safe=False)


@login_required
# 后台管理首页
def cn_backend(request):
    article_list=models.Article.objects.filter(user=request.user)
    return render(request,'backend/backend.html',{'article_list':article_list})

@login_required
def article_delete(request,id):
    book_obj = models.Article.objects.filter(pk=id).first()
    book_obj.delete()
    return redirect('/cn_backend/')

@login_required
def article_edit(request,id):
    article_obj = models.Article.objects.filter(pk=id).first()
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")

        # 过滤
        from bs4 import BeautifulSoup

        # 防止xss攻击,过滤script标签
        soup = BeautifulSoup(content, "html.parser")

        for tag in soup.find_all():
            # print(tag.name)
            if tag.name == "script":
                tag.decompose()

        desc = soup.text[0:150]
        # desc = desc.replace('<', '&lt;').replace('>', '&gt;')
        # 构建摘要数据,获取标签字符串的文本前150个符号

        models.Article.objects.filter(pk=id).update(title=title, desc=desc, content=str(soup), user=request.user)
        return redirect("/cn_backend/")

    return render(request, "backend/edit_article.html",{'article_obj': article_obj})


@login_required
def add_article(request):
    """
    后台管理的添加书籍视图函数
    :param request:
    :return:
    """
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")

        # 过滤
        from bs4 import BeautifulSoup

        # 防止xss攻击,过滤script标签
        soup=BeautifulSoup(content,"html.parser")

        for tag in soup.find_all():

            # print(tag.name)
            if tag.name=="script":
                # 删除
                tag.decompose()

        desc = soup.text[0:150]
        # desc = desc.replace('<', '&lt;').replace('>', '&gt;')
        # 构建摘要数据,获取标签字符串的文本前150个符号

        models.Article.objects.create(title=title,desc=desc,content=str(soup), user=request.user)
        return redirect("/cn_backend/")

    return render(request, "backend/add_article.html")

import os,json
from cnblog import settings
def upload(request):
    print(request.FILES)
    img=request.FILES.get('upload_img')
    path=os.path.join(settings.MEDIA_ROOT,'add_article',img.name)
    with open(path,'wb')as f:
        for line in img:
            f.write(line)
    response={'error':0,'url':'/media/add_article/%s'%img.name}


    return HttpResponse(json.dumps(response))

# def calendar(request):
#     return render(request ,'test.html')