from rest_framework import serializers
from goods.models import SPU


class SPUSerializer(serializers.ModelSerializer):
    """SPU序列化器"""
    class Meta:
        model = SPU
        fields = ('id', 'name')
