from django.urls import re_path as url
from market.apps.carts import views

urlpatterns = [
    # 省市区
    url(r'^carts/$', views.CartsView.as_view(), name='info'),
    url(r'^carts/selection/$', views.CartsSelectAllView.as_view()),
    url(r'^carts/simple/$', views.CartsSimpleView.as_view())
]