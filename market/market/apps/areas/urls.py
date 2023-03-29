from django.urls import re_path as url
from market.apps.areas import views

urlpatterns = [
    # 省市区
    url(r'^areas/$', views.AreasView.as_view()),
]