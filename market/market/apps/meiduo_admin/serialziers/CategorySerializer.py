from rest_framework import serializers

from goods.models import GoodsCategory


class CategorySerializer(serializers.ModelSerializer):
    """
    商品分类序列化器
    """
    class Meta:
        model = GoodsCategory
        fields = "__all__"
