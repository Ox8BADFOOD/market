from django.urls import include, re_path as url
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import statistical

urlpatterns = [
    # 登录方法
    url('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    url('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # --- 数据统计 ---
    url('^statistical/total_count/$', statistical.UserCountView.as_view())
]