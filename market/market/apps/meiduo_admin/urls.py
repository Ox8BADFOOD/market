from django.urls import include, re_path as url
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import statistical, user, sku, spec, spec_option, image, order
from rest_framework import routers

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
    # sku
    url('^skus/categories/$', sku.SKUView.as_view(actions={'get': 'categories'})),
    # spu关联商品
    url('^goods/simple/$', spec.SPUSpecsView.as_view(actions={'get': 'simple'})),
    # 所有SPU规格
    url('^goods/specs/simple/$', spec_option.SpecOptionView.as_view(actions={'get': 'simple'})),
    # 某一个SPU规格
    url('^goods/(?P<pk>\d+)/specs/$', spec.SPUSpecsView.as_view(actions={'get': 'specs'})),
    # 查询SKU
    url('^skus/simple/$', image.ImageView.as_view(actions={'get': 'simple'})),
]


router = routers.SimpleRouter()

# 产品规格
router.register(
    prefix=r'goods/specs',
    viewset=spec.SPUSpecsView,
    basename='specs'
)
urlpatterns += router.urls

# 规格选项
router.register(
    prefix=r'specs/options',
    viewset=spec_option.SpecOptionView,
    basename='specs_options'
)
urlpatterns += router.urls

# SKU图片
router.register(
    prefix=r'skus/images',
    viewset=image.ImageView,
    basename='images'
)
urlpatterns += router.urls

# sku
router.register(
    prefix=r'skus',
    viewset=sku.SKUView,
    basename='skus'
)
urlpatterns += router.urls

# 订单
router.register(
    prefix=r'orders',
    viewset=order.OrderView,
    basename='orders'
)
urlpatterns += router.urls

print("urlpatterns:%s" % urlpatterns)

