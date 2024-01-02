from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from goods.models import SKU, GoodsCategory
from meiduo_admin.serialziers.sku import SKUSerializer
from meiduo_admin.utils.PageNum import PageNum
from meiduo_admin.serialziers.CategorySerializer import CategorySerializer


class SKUView(ModelViewSet):
    serializer_class = SKUSerializer
    pagination_class = PageNum

    # 重写get_queryset方法，判断是否传递keyword查询参数
    def get_queryset(self):
        # 提取keyword
        keyword = self.request.query_params.get('keyword')

        if keyword == '' or keyword is None:
            return SKU.objects.all()
        else:
            return SKU.objects.filter(name__contains=keyword)

    def categories(self, request):
        """
        获取三级分类
        @type request: 请求
        """
        data = GoodsCategory.objects.filter(subs__id=None)
        ser = CategorySerializer(data, many=True)
        return Response(ser.data)
