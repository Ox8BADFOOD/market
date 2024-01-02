from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.viewsets import ModelViewSet
from meiduo_admin.serialziers.spu import SPUSerializer
from meiduo_admin.serialziers.spec import SPUSpecsSerializer
from goods.models import SPUSpecification, SPU
from meiduo_admin.utils.PageNum import PageNum
from meiduo_admin.serialziers.spu_specification import SPUSpecificationSerializer

class SPUSpecsView(ModelViewSet):
    """
    规格视图
    """
    serializer_class = SPUSpecsSerializer
    queryset = SPUSpecification.objects.all()
    pagination_class = PageNum

    def simple(self, requset: Request):
        """获取商品信息"""
        spus = SPU.objects.all()
        ser = SPUSerializer(spus, many=True)
        return Response(ser.data)

    def specs(self, request: Request, pk: int):
        """
        请求单个spu规格
        @type pk: spuid
        """
        spu = SPU.objects.get(id=pk)
        specs = spu.specs.all()
        ser = SPUSpecificationSerializer(specs, many=True)
        return Response(ser.data)
