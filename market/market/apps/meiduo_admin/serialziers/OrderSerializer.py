from rest_framework import serializers

from goods.models import SKU
from orders.models import OrderInfo, OrderGoods


class SKUSerializer(serializers.ModelSerializer):
    """
        商品sku表序列化器
    """

    class Meta:
        model = SKU
        fields = ('name', 'default_image')


class OrderGoodsSerializers(serializers.ModelSerializer):
    """
        订单商品序列化器
    """
    sku = SKUSerializer()

    class Meta:
        model = OrderGoods
        fields = ('count', 'price', 'sku')


class OrderSerializer(serializers.ModelSerializer):
    """
        订单序列化器
    """
    skus = OrderGoodsSerializers(many=True)

    class Meta:
        model = OrderInfo
        fields = '__all__'
