import logging
from datetime import datetime

from django import http
from django.core.handlers.wsgi import WSGIRequest
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render
from django.utils import timezone
from django.views import View
from goods import models, constants
from contents.utils import get_categories
from goods.models import SpecificationOption, GoodsVisitCount
from goods.utils import get_breadcrumb
from market.utils.response_code import *

logger = logging.getLogger('django')
class ListView(View):
    """商品列表"""

    def get(self, request: WSGIRequest, category_id: str, page_num: str):
        """
        提供商品列表
        :param request: 请求
        :param category_id 类别id
        :param page_num 页码
        """
        # 判断category_id是否正确
        try:
            category = models.GoodsCategory.objects.get(id=category_id)
        except models.GoodsCategory.DoesNotExist:
            return http.HttpResponseNotFound('GoodsCategory does not exist')

        # 接收sort参数：如果用户不传，就是默认的排序规则
        sort = request.GET.get('sort', 'default')

        # 查询商品频道分类
        categories = get_categories()
        # 查询面包屑导航
        breadcrumb = get_breadcrumb(category)

        # 按照排序规则查询该分类商品SKU信息
        if sort == 'price':
            # 按照价格由低到高
            sort_field = 'price'
        elif sort == 'hot':
            # 按照销量由高到低
            sort_field = '-sales'
        else:
            # 'price'和'sales'以外的所有排序方式都归为'default'
            sort = 'default'
            sort_field = 'create_time'

        skus = models.SKU.objects.filter(category=category, is_launched=True).order_by(sort_field)

        # 创建分页器：每页N条记录
        paginator = Paginator(skus, constants.GOODS_LIST_LIMIT)
        # 获取每页商品数据
        try:
            page_skus = paginator.page(page_num)
        except EmptyPage:
            # 如果page_num不正确，默认给用户404
            return http.HttpResponseNotFound('empty page')
        # 获取列表页总页数
        total_page = paginator.num_pages

        # 渲染页面
        context = {
            # 频道分类
            'categories': categories,
            # 面包屑导航
            'breadcrumb': breadcrumb,
            # 排序字段
            'sort': sort,
            # 第三级分类
            'category': category,
            # 分页后数据
            'page_skus': page_skus,
            # 总页数
            'total_page': total_page,
            # 当前页码
            'page_num': page_num,
            'category_id': category_id
        }
        return render(request=request, template_name='list.html', context=context)


class HotGoodsView(View):
    """商品热销排行"""

    def get(self, request: WSGIRequest, category_id: str):
        """
        提供商品热销排行JSON数据
        :param request: 请求
        :param category_id: 类别id
        :return:
        """

        # 获取sku
        skus = models.SKU.objects.filter(category_id=category_id, is_launched=True)
        # -加字段，代表反过来排序
        # [:2] 语法糖
        order_skus = skus.order_by('-sales')[:2]

        # 序列化
        hot_skus = []
        for sku in order_skus:
            hot_skus.append({
                'id': sku.id,
                'default_img': sku.default_image.url,
                'name': sku.name,
                'price': sku.price
            })

        return http.JsonResponse({
            'code': RETCODE.OK,
            'errmsg': err_msg[RETCODE.OK],
            'hot_skus': hot_skus
        })


class DetailView(View):
    """提供商品详情页"""

    def get(self, request: WSGIRequest, sku_id: str):
        # 获取当前sku的信息
        try:
            sku = models.SKU.objects.get(id=sku_id)
        except models.SKU.DoesNotExist:
            return render(request, '404.html')

        # 查询商品频道分类
        categories = get_categories()
        # 查询面包屑导航
        breadcrumb = get_breadcrumb(sku.category)

        # 构建当前商品的规格键
        sku_specs = sku.specs.order_by('spec_id')
        # sku的多个spec，映射成option规格选项id的数组
        sku_specs_map_option_ids = []
        for spec in sku_specs:
            # 一个sku规格对应一个option
            sku_specs_map_option_ids.append(spec.option.id)

        # 获取当前商品SPU下的所有SKU
        skus_incommon_spu = sku.spu.sku_set.all()

        # 构建不同规格参数（选项）的sku字典
        # spec_sku_map: 遍历skus_incommon_spu，{ tuple(sku.specs.map{(spec) in return spec.option.id;}) :sku的id, ... }
        spec_sku_map = {}
        for s in skus_incommon_spu:
            # 获取sku的规格参数
            s_specs = s.specs.order_by('spec_id')
            # 用于形成规格参数-sku字典的键
            key = []
            for spec in s_specs:
                key.append(spec.option.id)
            # 向规格参数-sku字典添加记录
            spec_sku_map[tuple(key)] = s.id

        # 获取当前商品的规格信息
        sku_spu_specs = sku.spu.specs.order_by('id')
        # 若当前sku的规格信息不完整，则不再继续
        if len(sku_specs_map_option_ids) < len(sku_spu_specs):
            return
        for index, sku_spu_spec in enumerate(sku_spu_specs):
            # 复制当前sku的规格键
            key = sku_specs_map_option_ids[:]
            # 该规格的选项
            sku_spu_spec_options = sku_spu_spec.options.all()
            for option in sku_spu_spec_options:
                # 在规格参数sku字典中查找符合当前规格的sku
                key[index] = option.id
                option.sku_id = spec_sku_map.get(tuple(key))
            sku_spu_spec.spec_options = sku_spu_spec_options

        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku': sku,
            'specs': sku_spu_specs,
        }
        return render(request=request, template_name='detail.html', context=context)


class DetailVisitView(View):
    """详情页分类商品访问量"""

    def post(self, request: WSGIRequest, category_id: str):

        """记录分类商品访问量"""
        try:
            category = models.GoodsCategory.objects.get(id=category_id)
        except models.GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden('缺少必要参数')

        t: datetime = timezone.localtime()
        today_str = '%d-%02d-%02d' % (t.year, t.month, t.day)
        today_date = datetime.strptime(today_str, '%Y-%m-%d')

        try:
            # 查询今天该类别的商品的访问量
            counts_data: GoodsVisitCount = category.goodsvisitcount_set.get(date=today_date)
        except models.GoodsVisitCount.DoesNotExist:
            # 如果该类别的商品在今天没有过访问记录，就新建一个访问记录
            counts_data = models.GoodsVisitCount()

        counts_data.category = category
        counts_data.count += 1
        try:
            counts_data.save()
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('服务器异常')

        return http.JsonResponse({
            'code': RETCODE.OK,
            'errmsg': 'OK'
        })



