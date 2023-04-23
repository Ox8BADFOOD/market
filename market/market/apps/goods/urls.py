from goods import views
from django.urls import re_path as url

urlpatterns = [
    # 注册
    url(r'^list/(?P<category_id>\d+)/(?P<page_num>\d+)/$', views.ListView.as_view()),
]

