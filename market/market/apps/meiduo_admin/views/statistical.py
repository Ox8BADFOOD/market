from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from datetime import date, timedelta

import market.apps.users.apps
from users.models import User
from rest_framework.response import Response
from goods.models import GoodsVisitCount
from meiduo_admin.serialziers.statistical import GoodsDailyVisitSerializer


class UserTotalCountView(APIView):
    """
    用户总量统计
    """

    # 权限指定
    # permission_classes = [IsAdminUser]
    def get(self, request):
        # 获取当天日期
        now_date = date.today()
        # 获取用户总量
        count = User.objects.all().count()
        # 返回结果
        return Response({
            'date': now_date,
            'count': count
        })


class UserDayCountView(APIView):
    """
    日增用户统计
    """

    # 权限指定
    # permission_classes = [IsAdminUser]
    def get(self, request):
        # 获取当天日期
        now_date = date.today()
        # 获取用户总量
        # 过滤查询 属性名称__比较运算符=值
        users = User.objects.filter(date_joined__gte=now_date)
        count = users.count()
        # 返回结果
        return Response({
            'date': now_date,
            'count': count
        })


class UserActiveCountView(APIView):
    """
    日活跃用户统计
    """

    # 权限指定
    # permission_classes = [IsAdminUser]
    def get(self, request):
        # 获取当天日期
        now_date = date.today()
        # 获取用户总量
        # 过滤查询 属性名称__比较运算符=值
        users = User.objects.filter(last_login__gte=now_date)
        count = users.count()
        # 返回结果
        return Response({
            'date': now_date,
            'count': count
        })


class UserOrderCountView(APIView):
    """
    日下单用户量统计
    """

    # 权限指定
    # permission_classes = [IsAdminUser]
    def get(self, request):
        # 获取当天日期
        now_date = date.today()
        # 获取用户总量
        # 关联过滤查询 关联模型类名小写__属性名__条件运算符=值
        users = User.objects.filter(orders__create_time__gte=now_date)
        count = users.count()
        # 返回结果
        return Response({
            'date': now_date,
            'count': count
        })


class UserMonthCountView(APIView):
    # 权限指定
    # permission_classes = [IsAdminUser]
    def get(self, request):
        # 获取当前日期
        now_date = date.today()
        # 获取一个月前的日期
        start_date = now_date - timedelta(29)
        # 遍历构建返回数据
        date_list = []

        for i in range(30):
            # 循环遍历获取当天日期
            index_date = start_date + timedelta(days=i)
            # 下一天日期
            nex_date = index_date + timedelta(days=i + 1)
            # 联合条件查询
            # 查询条件是大于当前日期index_date，小于明天日期的用户nex_date，得到当天用户量
            users = User.objects.filter(date_joined__gte=index_date, date_joined__lt=nex_date)
            count = users.count()
            date_list.append({
                'count': count,
                'date': index_date
            })

        return Response(date_list)


class GoodsDailyVisitView(APIView):

    def get(self, requset):
        """
        当日分类商品访问量
        """
        # 获取当天日期
        now_date = date.today()
        # 获取当天访问的商品分类数量信息
        data = GoodsVisitCount.objects.filter(date=now_date)
        # 序列化返回分类数量
        ser = GoodsDailyVisitSerializer(data, many=True)
        return Response(ser.data)
