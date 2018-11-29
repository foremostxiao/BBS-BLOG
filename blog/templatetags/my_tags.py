from django import template
from blog import models
from django.db.models import Avg, Max, Min, Sum, Count
#  自定义标签和过滤器--解决复用问题
register=template.Library()


@register.simple_tag()
def multi_tag(x,y):
    return x*y
# 引入模版语法 get_classification_style(username)函数的数据返回给classification.html


# @register.inclusion_tag("classification.html")
# def get_classification_style(username):
#     user_obj = models.UserInfo.objects.filter(username=username).first()
#     blog = user_obj.blog
#
#     cate_list=models.Category.objects.filter(blog=blog).values('pk').annotate(c=Count('article__title')).values_list('title','c')
#
#     #每一个标签以及对应得文章数
#     tag_list=models.Tag.objects.filter(blog=blog).values('pk').annotate(count=Count('article')).values_list('title','count')
#
#     # 单表分组查询
#     # 查询当前站点每一个年月的名称以及对应的文章数
#     # 方式一
#     date_list = models.Article.objects.filter(user=user_obj).extra(
#         select={'y_m_date': "date_format(create_time,'%%Y-%%m')"}).values('y_m_date').annotate(
#         c=Count('nid')).values_list('y_m_date', 'c')
#
#
#     return {"blog":blog,"cate_list":cate_list,"date_list":date_list,"tag_list":tag_list}