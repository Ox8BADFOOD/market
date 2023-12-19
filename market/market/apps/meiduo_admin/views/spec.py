from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from serialziers.SPU import SPUSerializer
from serialziers.spec import SpecsSerializer
from goods.models import SPUSpecification, SPU
from utils.PageNum import PageNum


class SpecsView(ModelViewSet):
    """
    规格视图
    """
    serializer_class = SpecsSerializer
    queryset = SPUSpecification.objects.all()
    pagination_class = PageNum

    def simple(self, requset):
        """获取商品信息"""
        spus = SPU.objects.all()
        ser = SPUSerializer(spus, many=True)
        return Response(ser.data)
