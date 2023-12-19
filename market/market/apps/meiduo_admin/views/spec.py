from rest_framework.viewsets import ModelViewSet
from serialziers.spec import SpecsSerializer
from goods.models import SPUSpecification
from utils.PageNum import PageNum


class SpecsView(ModelViewSet):
    """
    规格视图
    """
    serializer_class = SpecsSerializer
    queryset = SPUSpecification.objects.all()
    pagination_class = PageNum

