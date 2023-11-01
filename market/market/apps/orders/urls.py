from orders import views
from django.urls import re_path as url

urlpatterns = [
    # 订单

    # 结算页面
    url(r'^orders/settlement/$', views.OrderSettlementView.as_view(), name='settlement'),
    # 提交订单页面
    url(r'^orders/commit/$', views.OrderCommitView.as_view(), name='commit'),
    # 订单成功页面
    url(r'^orders/success/$', views.OrderSuccessView.as_view(), name='info'),
]