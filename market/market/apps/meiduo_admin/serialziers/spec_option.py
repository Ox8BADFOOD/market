from rest_framework import serializers
from goods.models import SpecificationOption


class SpecOptionSerializer(serializers.ModelSerializer):
    spec = serializers.StringRelatedField(read_only=True)
    spec_id = serializers.IntegerField()

    class Meta:
        model = SpecificationOption
        fields = '__all__'
