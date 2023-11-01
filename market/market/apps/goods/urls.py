from goods import views
from django.urls import re_path as url

urlpatterns = [
    # 注册
    url(r'^list/(?P<category_id>\d+)/(?P<page_num>\d+)/$', views.ListView.as_view(), name='list'),
    # 热销商品
    url(r'^hot/(?P<category_id>\d+)/$', views.HotGoodsView.as_view()),
    # 商品详情
    url(r'^detail/(?P<sku_id>\d+)/$', views.DetailView.as_view(), name='detail'),
    # 商品访问量统计 detail/visit/115/
    url(r'^detail/visit/(?P<category_id>\d+)/$', views.DetailVisitView.as_view())
]

