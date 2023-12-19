from rest_framework.generics import ListCreateAPIView
from serialziers.user import UserSerializer, UserAddSerializer
from users.models import User
from utils.PageNum import PageNum


class UserView(ListCreateAPIView):
    pagination_class = PageNum

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        else:
            return UserAddSerializer

    # 重写get_queryset方法，根据前端是否传递keyword值返回不同查询结果
    def get_queryset(self):
        # 获取前端传递的keyword值
        kwd = self.request.query_params.get(key='keyword')
        # 如果keyword是空字符，则说明要获取所有用户数据
        if kwd is '' or kwd is None:
            return User.objects.all()
        else:
            return User.objects.filter(username=kwd)