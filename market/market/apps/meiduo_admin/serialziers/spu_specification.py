from rest_framework import serializers
from goods.models import SPUSpecification


class SPUSpecificationSerializer(serializers.ModelSerializer):
    """
    SPU规格序列化器
    """
    class Meta:
        model = SPUSpecification
        fields = "__all__"
