"""market URL Configuration

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
from django.urls import path, include, re_path as url

urlpatterns = [
    path('admin/', admin.site.urls),
    # include需要两个参数，arg和namespace, 当namespace不为空时，arg参数必须是一个2元组，
    # 除了urlpatterns不能为空之外，app_name也必须填写
    url(r'^', include(('users.urls', 'users'), namespace='users')),
    url(r'^', include('verifications.urls')),
    url(r'^', include('areas.urls')),
    url(r'^', include(('contents.urls', 'index'), namespace='contents')),

]
