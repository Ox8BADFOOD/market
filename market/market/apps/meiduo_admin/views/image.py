from rest_framework.viewsets import ModelViewSet
from serialziers.ImageSerializer import ImageSerializer
from goods.models import SKUImage
from utils.PageNum import PageNum


class ImageView(ModelViewSet):
    serializer_class = ImageSerializer
    queryset = SKUImage.objects.all()
    pagination_class = PageNum
