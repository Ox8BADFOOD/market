from rest_framework.viewsets import ModelViewSet
from goods.models import SKU
from serialziers.sku import SKUSerializer
from utils.PageNum import PageNum


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
            return SKU.objects.filter(name=keyword)
