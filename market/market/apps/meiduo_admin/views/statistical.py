from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from datetime import date

import market.apps.users.apps
from users.models import User
from rest_framework.response import Response

class UserCountView(APIView):
    """
    用户总量统计
    """
    # 权限指定
    # permission_classes = [IsAdminUser]
    def get(self, request):
        # 活期当天日期
        new_date = date.today()
        # 获取用户总量
        count = User.objects.all().count()
        # 返回结果
        return Response({
            'date': new_date,
            'count': count
        })