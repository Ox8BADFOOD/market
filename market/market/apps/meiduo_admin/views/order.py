from rest_framework.viewsets import ReadOnlyModelViewSet
from orders.models import OrderInfo
from serialziers.OrderSerializer import OrderSerializer
from utils.PageNum import PageNum


class OrderView(ReadOnlyModelViewSet):
    queryset = OrderInfo.objects.all()
    serializer_class = OrderSerializer
    pagination_class = PageNum
