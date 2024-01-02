from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from meiduo_admin.serialziers.ImageSerializer import ImageSerializer
from goods.models import SKUImage, SKU
from meiduo_admin.utils.PageNum import PageNum
from rest_framework.request import Request
from meiduo_admin.serialziers.sku import SKUSerializer


class ImageView(ModelViewSet):
    serializer_class = ImageSerializer
    queryset = SKUImage.objects.all()
    pagination_class = PageNum

    def simple(self, request: Request) -> object:
        """
        查询SKU信息
        @param request:
        """
        data = SKU.objects.all()
        ser = SKUSerializer(data, many=True)
        return Response(ser.data)
