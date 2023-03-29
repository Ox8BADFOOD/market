from django.urls import re_path as url
from market.apps.contents import views

urlpatterns = [
    # 注册
    url(r'^', views.IndexView.as_view(), name='index'),
]