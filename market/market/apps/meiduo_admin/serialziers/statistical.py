from rest_framework import serializers
from goods.models import GoodsVisitCount


class GoodsDailyVisitSerializer(serializers.ModelSerializer):
    # 指定返回分类，以名称展示
    category = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = GoodsVisitCount
        fields = ('count', 'category')
