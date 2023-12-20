from rest_framework.viewsets import ModelViewSet
from serialziers.spec_option import SpecOptionSerializer
from goods.models import SpecificationOption
from utils.PageNum import PageNum
from rest_framework.response import Response
from rest_framework.request import Request
from goods.models import SPUSpecification
from serialziers.spu_specification import SPUSpecificationSerializer
class SpecOptionView(ModelViewSet):
    """
     规格选项表的增删改查
    """
    serializer_class = SpecOptionSerializer
    queryset = SpecificationOption.objects.all()
    pagination_class = PageNum

    def simple(self, request: Request) -> object:
        """
        查询所有规格
        @param request:
        """
        spu_specifications = SPUSpecification.objects.all()
        ser = SPUSpecificationSerializer(spu_specifications, many=True)
        return Response(ser.data)
