from django.urls import include, re_path as url
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import statistical, user

urlpatterns = [
    # 登录方法
    url('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    url('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # --- 数据统计 ---
    # 用户总量统计
    url('^statistical/total_count/$', statistical.UserTotalCountView.as_view()),
    # 日增用户统计
    url('^statistical/day_increment/$', statistical.UserDayCountView.as_view()),
    # 日活跃用户统计
    url('^statistical/day_active/$', statistical.UserActiveCountView.as_view()),
    # 日下单用户量统计
    url('^statistical/day_orders/$', statistical.UserOrderCountView.as_view()),
    # 月增用户统计
    url('^statistical/month_increment/$', statistical.UserMonthCountView.as_view()),
    # 日分类商品访问量
    url('^statistical/goods_day_views/$', statistical.GoodsDailyVisitView.as_view()),

    # 用户管理
    url('^users/$', user.UserView.as_view()),
]
