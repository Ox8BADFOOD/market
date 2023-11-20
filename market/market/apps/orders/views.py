import json
from _decimal import Decimal
from datetime import datetime

from django import http
from django.http import HttpRequest
from django.shortcuts import render
from django.utils import timezone

from django.views import View
from django_redis import get_redis_connection

from goods.models import SKU
from market.utils.response_code import RETCODE
from market.utils.views import LoginRequiredMixin
from users.models import Address
from orders.models import OrderInfo, OrderGoods
from django.db import transaction
from logging import getLogger
# Create your views here.

logger = getLogger("django")

class OrderSettlementView(LoginRequiredMixin, View):
    """结算订单页面"""

    def get(self, request: HttpRequest):
        """提供订单结算页面"""
        # 获取登录用户
        user = request.user
        # 查询地址信息
        try:
            addresses = Address.objects.filter(user=user, is_delete=False)
        except Address.DoesNotExist:
            addresses = None

        # 从Redis购物车中查询出被勾选的商品信息
        redis_conn = get_redis_connection(alias='carts')
        redis_cart = redis_conn.hgetall('carts_%s' % user.id)
        cart_selected = redis_conn.smembers('selected_%s' % user.id)

        cart = {}
        for sku_id in cart_selected:
            key: int = int(sku_id)
            val: int = int(redis_cart[sku_id])
            cart[key] = val


        # 准备初始值
        total_count = 0
        total_amount = Decimal(0.00)
        # 查询商品信息
        skus = SKU.objects.filter(id__in=cart.keys())
        for sku in skus:
            sku.count = cart[sku.id]
            sku.amount = sku.count * sku.price
            total_count += sku.count
            total_amount += sku.amount

        # 补充运费
        freight = Decimal('10.00')

        context = {
            'addresses': addresses,
            'skus': skus,
            'total_count': total_count,
            'total_amount': total_amount,
            'freight': freight,
            'payment_amount': total_amount + freight
        }
        return render(request=request, template_name='place_order.html', context=context)


class OrderCommitView(LoginRequiredMixin, View):
    """订单提交"""

    def post(self, request: HttpRequest):
        """保存订单信息和订单商品信息"""
        # 获取当前要保存的订单数据
        json_dict: dict = json.loads(request.body.decode())
        address_id = json_dict.get('address_id')
        pay_method = json_dict.get('pay_method')

        # 校验参数
        if not all([address_id, pay_method]):
            return http.HttpResponseForbidden('缺少必要参数')

        # 判断address_id是否合法
        try:
            address = Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            return http.HttpResponseForbidden('参数address_id错误')

        # 判断pay_method是否合法
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return http.HttpResponseForbidden('参数pay_method错误')

        user = request.user
        # 当前时间
        local_time: datetime = timezone.localtime()
        # 生成订单编号：年月日时分秒+用户编号
        order_id = local_time.strftime('%Y%m%d%H%M%S')+('%09d' % user.id)

        with transaction.atomic():
            save_id = transaction.savepoint()

            try:
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=0,
                    total_amount=Decimal(0.00),
                    freight=Decimal(10.00),
                    pay_method=pay_method,
                    status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'] if pay_method == OrderInfo.PAY_METHODS_ENUM[
                        'ALIPAY'] else OrderInfo.ORDER_STATUS_ENUM['UNSEND']
                )
                redis_conn = get_redis_connection('carts')
                redis_cart = redis_conn.hgetall('carts_%s' % user.id)
                selected = redis_conn.smembers('selected_%s' % user.id)
                carts = {}
                for sku_id in selected:
                    carts[int(sku_id)] = int(redis_cart[sku_id])
                sku_ids = carts.keys()

                # 遍历购物车中被勾选的商品信息
                for sku_id in sku_ids:
                    while True:
                        # 查询SKU信息
                        sku = SKU.objects.get(id=sku_id)

                        # 原始库存
                        origin_stock = sku.stock
                        # 原始销量
                        origin_sale = sku.sales

                        # 判断sku库存
                        sku_count = carts[sku.id]
                        if sku_count > origin_stock:
                            transaction.savepoint_rollback(sid=save_id)
                            return http.JsonResponse({'code': RETCODE.STOCKERR, 'errmsg': '库存不足'})

                        # 乐观锁更新库存和销量
                        new_stock = origin_stock - sku_count
                        new_sales = origin_sale + sku_count
                        result = SKU.objects.filter(id=sku_id, stock=origin_stock).update(stock=new_stock,sales=new_sales)
                        if result == 0:
                            continue

                        # 修改spu销量
                        sku.spu.sales += sku_count
                        sku.spu.save()

                        # 保存订单信息 OrderGoods
                        OrderGoods.objects.create(
                            order=order,
                            sku=sku,
                            count=sku_count,
                            price=sku.price,
                        )

                        # 保存订单商品中总价和总数量
                        order.total_count += sku_count
                        order.total_amount += (sku_count * sku.price)

                        # 下单成功跳出循环
                        break

                # 添加邮费和保存订单信息
                order.total_amount += order.freight
                order.save()
            except Exception as e:
                logger.error(e)
                transaction.savepoint_rollback(sid=save_id)
                return http.JsonResponse({
                    'code': RETCODE.DBERR,
                    'errmsg': '下单失败'
                })

        # 保存订单数据成功，显式的提交一次事务
        transaction.savepoint_commit(sid=save_id)

        # 清除Redis里购物车的商品
        pl = redis_conn.pipeline()
        pl.hdel('carts_%s' % user.id, *selected)
        pl.srem('selected_%s' % user.id, *selected)
        pl.execute()

        # 响应提交订单结果
        return http.JsonResponse({'code': RETCODE.OK,
                                  'errmsg': '下单成功',
                                  'order_id': order_id})


class OrderSuccessView(LoginRequiredMixin, View):
    """提交订单成功"""

    def get(self, request: HttpRequest):
        order_id = request.GET.get('order_id')
        payment_amount = request.GET.get('payment_amount')
        pay_method = request.GET.get('pay_method')

        context = {
            'order_id': order_id,
            'payment_amount': payment_amount,
            'pay_method': pay_method,
        }
        return render(request, 'order_success.html', context)
