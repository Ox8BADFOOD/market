from rest_framework import serializers

from goods.models import SKUSpecification, SKU


class SKUSpecificationSerializer(serializers.ModelSerializer):
    """
        SKU规格表序列化器
    """
    spec_id = serializers.IntegerField(read_only=True)
    option_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = SKUSpecification
        fields = ('spec_id', 'option_id')


class SKUSerializer(serializers.ModelSerializer):
    """
        获取sku表信息的序列化器
    """
    spu = serializers.StringRelatedField(read_only=True)
    # 指定所关联的spu表信息
    spu_id = serializers.IntegerField()
    # 指定分类信息
    category_id = serializers.IntegerField()
    # 指定分类信息
    category_id = serializers.IntegerField()
    category = serializers.StringRelatedField(read_only=True)
    # 指定所关联的选项信息 关联嵌套返回
    specs = SKUSpecificationSerializer(read_only=True, many=True)

    class Meta:
        model = SKU
        fields = '__all__'
