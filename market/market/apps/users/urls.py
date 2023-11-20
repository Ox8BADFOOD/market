from django.urls import re_path as url
from market.apps.users import views

urlpatterns = [
    # 注册
    url(r'^register/$', views.RegisterView.as_view(), name='register'),
    #  登录
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    #  登出
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    #  用户名重复注册
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.UserNameCountView.as_view()),
    # 手机号重复注册
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
    # 用户信息
    url(r'^info/$', views.UserInfoView.as_view(), name='info'),
    # 邮箱
    url(r'^emails/$', views.EmailView.as_view()),
    # 验证邮箱/emails/verification/
    url(r'^emails/verification/$', views.VerifyEmailView.as_view()),
    # 展示用户地址
    url(r'^addresses/$', views.AddressView.as_view(), name='address'),
    # /addresses/create/
    url(r'^addresses/create/$', views.AddressView.as_view(), name='address'),
    # 编辑地址
    url(r'^addresses/(?P<address_id>\d+)/$', views.UpdateDestroyAddressView.as_view()),
    # 设置默认地址
    url(r'^addresses/(?P<address_id>\d+)/default/$', views.DefaultAddressView.as_view()),
    # 修改标题
    url(r'^addresses/(?P<address_id>\d+)/title/$', views.UpdateTitleAddressView.as_view()),
    # 修改密码
    url(r'^resetpwd/$', views.ChangePasswordView.as_view(), name="pass"),
    # 用户浏览记录
    url(r'^browse_histories/$', views.UserBrowseHistory.as_view()),
    # 我的订单页面
    url(r'^orders/info/(?P<page_num>\d+)/$', views.UserOrderInfoView.as_view(), name="orders"),
]


