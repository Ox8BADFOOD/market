from django.db import transaction
from rest_framework import serializers
from goods.models import SKUSpecification, SKU
from celery_tasks.static_file.task import get_detail_html

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
    category = serializers.StringRelatedField(read_only=True)
    # 指定所关联的选项信息 关联嵌套返回
    specs = SKUSpecificationSerializer(read_only=True, many=True)

    # 指定只读字段
    # read_only_fields = ()

    class Meta:
        model = SKU
        fields = '__all__'

    def create(self, validated_data):
        specs = self.context['request'].data.get('specs')
        # 开启事务
        with transaction.atomic():
            save_point = transaction.savepoint()
            try:
                # 保存sku表
                sku = SKU.objects.create(**validated_data)
                # 保存sku具体规格表
                for spec in specs:
                    SKUSpecification.objects.create(spec_id=spec['spec_id'],
                                                    option_id=spec['option_id'],
                                                    sku=sku)
            except:
                # 回滚
                transaction.savepoint_rollback(save_point)
                raise serializers.ValidationError('数据库保存失败')
            else:
                transaction.savepoint_commit(save_point)
                # 生成详情页静态页面
                get_detail_html.delay(sku.id)
                return sku

    def update(self, instance, validated_data):
        specs = self.context['request'].data.get('specs')
        # 开启事务
        with transaction.atomic():
            save_point = transaction.savepoint()
            try:
                # 修改sku表
                SKU.objects.filter(id=instance.id).update(**validated_data)
                # 修改sku具体规格表
                for spec in specs:
                    SKUSpecification.objects.filter(sku=instance).update(**spec)
            except:
                # 回滚
                transaction.savepoint_rollback(save_point)
                raise serializers.ValidationError('保存失败')
            else:
                # 提交
                transaction.savepoint_commit(save_point)
                # 生成详情页静态页面
                get_detail_html.delay(instance.id)
                return instance
