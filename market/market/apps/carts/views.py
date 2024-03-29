import base64
import pickle
from django import http
import json

from django.http import HttpRequest
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection

from carts import constants
from goods import models
from market.utils.response_code import RETCODE


class CartsView(View):
    """购物车管理"""

    def post(self, request: HttpRequest):
        """添加购物车"""
        # 接收和校验参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)

        # 判断参数是否齐全
        if not all([sku_id, count]):
            return http.HttpResponseForbidden('缺少必传参数')

        # 判断sku_id是否存在
        try:
            models.SKU.objects.get(id=sku_id)
        except models.SKU.DoesNotExist:
            return http.HttpResponseForbidden('商品不存在')

        # 判断count是否位数字
        try:
            count = int(count)
        except Exception:
            return http.HttpResponseForbidden('参数count有误')

        # 判断selected是否为bool值
        if selected:
            if not isinstance(selected, bool):
                return http.HttpResponseForbidden('参数selected有误')

        # 判断用户是否登录
        user = request.user
        if user.is_authenticated:
            # 用户已登录，操作redis购物车
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            # 新增购物车数据
            pl.hincrby('carts_%s' % user.id, sku_id, count)
            # 新增选中的状态
            if selected:
                pl.sadd('selected_%s' % user.id, sku_id)
            # 执行
            pl.execute()
            # 响应结果
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加购物车成功'})
        else:
            # 用户未登录，操作cookie购物车
            cart_str = request.COOKIES.get('carts')
            # 如果用户操作过购物车
            if cart_str:
                # base64.b64deocde()将base64编码后的bytes类型数据进行解码，返回解码后的bytes类型数据。
                val: bytes = base64.b64decode(cart_str.encode())
                # pickle.loads()将bytes类型数据反序列化为python数据
                # pickle.dumps()将Python数据序列化为bytes类型数据。
                cart_dict = pickle.loads(val)
            else:
                cart_dict = {}

            # 判断要加入购物车的商品是否已经在购物车中,如有相同商品，累加求和，反之，直接赋值
            if sku_id in cart_dict:
                # 累加求和
                origin_count = cart_dict[sku_id]['count']
                count += origin_count
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }

            # 将字典转成bytes,再将bytes转成base64的bytes,最后将bytes转字符串
            cookie_cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()

            # 创建响应对象
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加购物车成功'})
            # 响应结果并将购物车数据写入到cookie
            response.set_cookie('carts', cookie_cart_str, max_age=constants.CARTS_COOKIE_EXPIRES)
            return response

    def get(self, request: HttpRequest):
        user = request.user
        if user.is_authenticated:
            # 用户已登录，查询redis购物车
            redis_conn = get_redis_connection('carts')
            # 获取redis中的购物车数据
            redis_cart = redis_conn.hgetall('carts_%s' % user.id)
            # 获取redis中的选中状态
            cart_selected = redis_conn.smembers('selected_%s' % user.id)

            # 将redis中的数据构造成跟cookie中的格式一致，方便统一查询
            cart_dict = {}
            for sku_id, count in redis_cart.items():
                cart_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in cart_selected
                }
        else:
            # 用户未登录，查询cookies购物车
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                # 将cart_str转成bytes
                bts = cart_str.encode()
                # 再将bytes转成base64的bytes
                bts64 = base64.b64decode(bts)
                # 最后将bytes转字典
                cart_dict = pickle.loads(bts64)
            else:
                cart_dict = {}

        # 构造购物车渲染数据
        sku_ids = cart_dict.keys()
        skus = models.SKU.objects.filter(id__in=sku_ids)
        cart_skus = []
        for sku in skus:
            cart_skus.append({
                'id': sku.id,
                'name': sku.name,
                'count': cart_dict.get(sku.id).get('count'),
                'selected': str(cart_dict.get(sku.id).get('selected')),
                'default_image_url': sku.default_image.url,
                'price': str(sku.price),
                'amount': str(sku.price * cart_dict.get(sku.id).get('count')),
            })
        context = {
            'cart_skus': cart_skus,
        }

        return render(request, 'cart.html', context)

    def put(self, request: HttpRequest):
        """修改购物车"""
        # 接受参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)

        # 判断参数是否齐全
        if not all([sku_id, count]):
            return http.HttpResponseForbidden('缺少必传参数')

        # 判断sku_id是否存在
        try:
            sku = models.SKU.objects.get(id=sku_id)
        except models.SKU.DoesNotExist:
            return http.HttpResponseForbidden('商品sku_id不存在')

        try:
            count = int(count)
        except Exception:
            return http.HttpResponseForbidden('参数count有误')

        if selected:
            if not isinstance(selected, bool):
                return http.HttpResponseForbidden('参数selected有误')

        user = request.user
        if user.is_authenticated:
            # 用户已登录，修改Redis购物车
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            # 因为接口设计为幂等的，直接覆盖
            pl.hset('carts_%s' % user.id, sku_id, count)
            # 是否选中
            if selected:
                pl.sadd('selected_%s' % user.id, sku_id)
            else:
                pl.srem('selected_%s' % user.id, sku_id)
            pl.execute()

            # 创建响应对象
            cart_sku = {
                'id': sku_id,
                'count': count,
                'selected': selected,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price,
                'amount': sku.price * count,
            }
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '修改购物车成功', 'cart_sku': cart_sku})
        else:
            # 用户未登录，修改cookie购物车
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                # 将cart_str转成bytes,再将bytes转成base64的bytes,最后将bytes转字典
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}
            # 因为接口设计为幂等的，直接覆盖
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }
            # 数据序列化为bytes类型数据
            bts: bytes = pickle.dumps(cart_dict)
            # 再将bytes转成base64的bytes,
            bts64 = base64.b64encode(bts)
            # 最后将bytes转字符串
            cookie_cart_str = bts64.decode()

            # 创建响应对象
            cart_sku = {
                'id': sku_id,
                'count': count,
                'selected': selected,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price,
                'amount': sku.price * count,
            }

            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '修改购物车成功', 'cart_sku': cart_sku})
            response.set_cookie('carts', value=cookie_cart_str, max_age=constants.CARTS_COOKIE_EXPIRES)
            return response


    def delete(self, request):
        """删除购物车"""
        # 接收和校验参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')

        # 判断sku_id是否存在
        try:
            models.SKU.objects.get(id=sku_id)
        except models.SKU.DoesNotExist:
            return http.HttpResponseForbidden('商品不存在')

        # 判断用户是否登录
        user = request.user
        if user.is_authenticated:
            # 用户未登录，删除redis购物车
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            # 删除键，就等价于删除了整条记录
            pl.hdel('carts_%s' % user.id, sku_id)
            pl.srem('selected_%s' % user.id, sku_id)
            pl.execute()

            # 删除结束后，没有响应的数据，只需要响应状态码即可
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除购物车成功'})
        else:
            # 用户未登录，删除cookie购物车
            # 用户未登录，删除cookie购物车
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                # 将cart_str转成bytes,再将bytes转成base64的bytes,最后将bytes转字典
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}

            # 创建响应对象
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除购物车成功'})
            if sku_id in cart_dict:
                del cart_dict[sku_id]
                # 将字典转成bytes,再将bytes转成base64的bytes,最后将bytes转字符串
                cookie_cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
                # 响应结果并将购物车数据写入到cookie
                response.set_cookie('carts', cookie_cart_str, max_age=constants.CARTS_COOKIE_EXPIRES)
            return response

class CartsSelectAllView(View):
    """全选购物车"""

    def put(self, request: HttpRequest):

        # 接受和校验参数
        json_dict_str: str = request.body.decode()
        """Deserialize ``fp`` (a ``.read()``-supporting file-like object containing
            a JSON document) to a Python object.
            """
        # json_dic = json.load()
        json_dic: dict = json.loads(json_dict_str)
        selected = json_dic.get('selected', True)

        # 校验参数
        if selected:
            if not isinstance(selected, bool):
                return http.HttpResponseForbidden('参数selected有误')

        # 判断用户是否登录
        user = request.user
        if user is not None and user.is_authenticated:
            # 用户已经登录，操作Redis购物车
            redis_conn = get_redis_connection('carts')
            cart: dict = redis_conn.hgetall('carts_%s' % user.id)
            sku_id_list = cart.keys()
            if selected:
                # 全选
                redis_conn.sadd('selected_%s' % user.id, *sku_id_list)
            else:
                # 取消全选
                redis_conn.srem('selected_%s' % user.id, *sku_id_list)
            return http.JsonResponse(data={
                'code': RETCODE.OK,
                'errmsg': '全选购物车成功'
            })
        else:
            # 用户未经登录，操作cookie购物车
            cart_cookies_str: str = request.COOKIES.get('carts')
            response = http.JsonResponse({
                'code': RETCODE.OK,
                'errmsg': '全选购物车成功'
            })
            if cart_cookies_str is not None:
                bts: bytes = cart_cookies_str.encode()
                bts64: bytes = base64.b64decode(bts)
                cart: dict = pickle.loads(bts64)
                for sku_id in cart:
                    cart[sku_id]['selected'] = selected
                cookie_cart = base64.b64encode(pickle.dumps(cart)).decode()
                response.set_cookie(key='carts', value=cookie_cart, max_age=constants.CARTS_COOKIE_EXPIRES)
            return response

class CartsSimpleView(View):
    """商品页面右上角购物车"""

    def get(self, request: HttpRequest):
        # 判断用户是否登录了
        user = request.user
        if user.is_authenticated:
            # 用户已登录，查询Redis购物车
            redis_conn = get_redis_connection('carts')
            redis_cart = redis_conn.hgetall('carts_%s' % user.id)
            cart_selected = redis_conn.smembers('selected_%s' % user.id)
            cart_dict = {}
            for sku_id, count in redis_cart.items():
                cart_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in cart_selected
                }
        else:
            cart_str: str = request.COOKIES.get('carts')
            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}

        # 构造简单购物车JSON数据
        cart_skus = []
        sku_ids = cart_dict.keys()
        skus = models.SKU.objects.filter(id__in=sku_ids)

        for sku in skus:
            cart_skus.append({
                'id': sku.id,
                'name': sku.name,
                'count': cart_dict[sku.id].get('count'),
                'default_image_url': sku.default_image.url
            })

        return http.JsonResponse({
            'code': RETCODE.OK,
            'errmsg': 'OK',
            'cart_skus': cart_skus
        })
