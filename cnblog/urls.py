"""cnblog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path
from django.views.static import serve
from cnblog import settings
from django.urls import include
from blog import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login,name='log'),
    path('index/', views.index),
    path('logout/', views.logout),
    re_path('^$', views.index),
    path('register/', views.register),
    path('get_validCode_img/', views.get_validCode_img),
    # path('calendar/', views.calendar),


    # 后台管理url
    re_path('cn_backend/$',views.cn_backend),
    re_path('cn_backend/add_article/$',views.add_article),
    # 后台文本编辑器上传功能
    path('upload/',views.upload),
    re_path(r"^article/(\d+)/delete", views.article_delete),
    re_path(r"^article/(\d+)/edit", views.article_edit),




    # 点赞
    path('digg/',views.digg),

    path("comment/", views.comment),
    # 获取评论树相关数据
    path("get_comment_tree/", views.get_comment_tree),



    # media
    re_path(r'media/(?P<path>.*)$',serve,{'document_root':settings.MEDIA_ROOT}),

    # 文章详情页
    # re_path('(?P<username>\w)/(?P<article_id>\d+)$',views.article_detail),
    re_path('^(?P<username>\w+)/articles/(?P<article_id>\d+)$', views.article_detail),

    # 关于个人站点的url
    re_path("^(?P<username>\w+)/$", views.home_site),  # home_site(reqeust,username="yuan")
    #个人站点下的跳转
    re_path('^(?P<username>\w+)/(?P<condition>tag|category|archive)/(?P<param>.*)/$', views.home_site),
    # home_site(reqeust,username="yuan",condition='tag',param='python')

]
