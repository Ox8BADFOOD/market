from rest_framework import serializers
from goods.models import SPUSpecification
from meiduo_admin.serialziers.spec_option import SpecOptionSerializer


class SPUSpecificationSerializer(serializers.ModelSerializer):
    """
    SPU规格序列化器
    """
    options = SpecOptionSerializer(many=True)

    class Meta:
        model = SPUSpecification
        fields = "__all__"
