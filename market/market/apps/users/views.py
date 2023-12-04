import json
import logging
import re
from django.contrib.auth import login, authenticate, logout
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django import http
from django_redis import get_redis_connection
from pymysql import DatabaseError

from carts.utils import merge_cart_cookie_to_redis
from celery_tasks.email.tasks import send_verify_email
from goods import models
from market.utils.response_code import RETCODE
from market.utils.views import LoginRequiredMixin, LoginRequiredJSONMixin
from users.models import User, Address
from . import constants

# 创建日志输出器
from users.utils import generate_verify_email_url, check_verify_email_token

logger = logging.getLogger('django')


class RegisterView(View):
    """用户注册"""

    def get(self, request):
        """
        提供注册界面
        :param request: 请求对象
        :return: 注册界面
        """
        return render(request, 'register.html')

    def post(self, request):
        """
        实现用户注册
        :param request: 请求对象
        :return: 注册结果
        """
        username = request.POST.get("username")
        password = request.POST.get("password")
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        allow = request.POST.get('allow')

        # 判断参数是否齐全
        if not all([username, password, password2, mobile, allow]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 判断用户名是否是5-20个字符
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('请输入5-20个字符的用户名')
        # 判断密码是否是8-20个数字
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20位的密码')
        # 判断两次密码是否一致
        if password != password2:
            return http.HttpResponseForbidden('两次输入的密码不一致')
        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('请输入正确的手机号码')
        # 判断是否勾选用户协议
        if allow != 'on':
            return http.HttpResponseForbidden('请勾选用户协议')
        # # 保存注册数据
        try:
            user: User = User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError:
            return render(request, 'register.html', {'register_errmsg': '注册失败'})

        """
        Django用户认证系统提供了login()方法。
        封装了写入session的操作，帮助我们快速登入一个用户，并实现状态保持。
        django.contrib.auth.__init__.py文件中：
        login(request, user, backend=None)
        """
        # 登入用户，实现状态保持
        login(request, user)
        # 响应注册结果
        return redirect(reverse('contents:index'))


class LoginView(View):
    """用户登录"""

    def get(self, request):
        """
         提供注册界面
         :param request: 请求对象
         :return: 注册界面
         """
        return render(request, 'login.html')

    def post(self, request: HttpRequest):
        """
        实现登录逻辑
        :param request: 请求对象
        :return: 登录结果
        """
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')

        # 校验参数
        # 判断参数是否齐全
        if not all([username, password]):
            return http.HttpResponseForbidden('缺少必填参数')

        # 判断用户名是否是5-20个字符
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('请输入正确的用户名或手机号')

        # 判断密码是否是8-20个数字
        if not re.match(r'^[0-9a-zA-Z]{8,20}$', password):
            return http.HttpResponseForbidden('密码只能包含数字和字母，最少8位，最长20位.')

        # 认证登录用户
        user = authenticate(request=request, username=username, password=password)
        if user is None:
            return render(request, 'login.html', {'account_errmsg': '用户名或密码错误'})

        # 实现登录状态保持
        login(request, user)
        # 设置状态保持的周期
        if remembered != 'on':
            # 没有记住用户：浏览器会话结束就过期
            request.session.set_expiry(0)
        else:
            # 记住用户：None表示两周后过期
            request.session.set_expiry(None)

        # 响应登录结果
        nextParam = request.GET.get('next')
        if nextParam:
            resp = redirect(nextParam)
        else:
            resp = redirect(reverse('contents:index'))

        resp.set_cookie(key="username", value=user.username, max_age=3600 * 24 * 15)

        resp = merge_cart_cookie_to_redis( request, request.user, resp)
        return resp


class UserNameCountView(View):
    """判断是否重复注册"""

    def get(self, request: HttpRequest, username: str):
        """
        :param request: 请求对象
        :param username: 用户名
        :return: JSON
        """
        count: int = User.objects.filter(username=username).count()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})


class MobileCountView(View):
    """判断手机号是否重复注册"""

    def get(self, request, mobile):
        """
        :param request: 请求对象
        :param mobile: 手机号
        :return: JSON
        """
        count: int = User.objects.filter(mobile=mobile).count()
        return http.JsonResponse({
            'code': RETCODE.OK,
            'errmsg': 'OK',
            'count': count
        })


class LogoutView(View):
    """登出"""

    def get(self, request: HttpRequest):
        logout(request)
        resp = redirect(reverse('contents:index'))
        resp.delete_cookie('username')
        return resp


class UserInfoView(LoginRequiredMixin, View):
    """用户信息"""

    def get(self, request: HttpRequest):
        """提供个人信息界面"""
        context = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active
        }
        return render(request, 'user_center_info.html', context=context)


class EmailView(LoginRequiredJSONMixin, View):
    """添加邮箱"""

    def put(self, request: HttpRequest):
        """实现添加邮箱逻辑"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        email = json_dict.get("email")

        # 校验参数
        if not email:
            return http.HttpResponseForbidden('缺少email参数')
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return http.HttpResponseForbidden('参数email有误')

        # 赋值email字段
        try:
            request.user.email = email
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '添加邮箱失败'})

        # 异步发送验证邮件
        verify_url = generate_verify_email_url(user=request.user)
        send_verify_email.delay(to_email=email, verify_url=verify_url)

        # 响应添加邮箱结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加邮箱成功'})


class VerifyEmailView(View):

    def get(self, request: HttpRequest):
        """
        验证邮箱
        :param request:
        :return:
        """
        token = request.GET.get(key="token")
        if not token:
            return http.HttpResponseBadRequest('缺少token')

        user = check_verify_email_token(token)
        if not user:
            return http.HttpResponseForbidden(content='无效的token')

        try:
            user.email_active = True
            user.save()
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('激活邮件失败')

        return redirect(to=reverse("users:info"))


class AddressView(LoginRequiredMixin, View):
    """用户收货地址"""

    def get(self, request: HttpRequest):
        """提供收货地址界面"""
        login_user = request.user
        addresses = Address.objects.filter(user=login_user, is_delete=False)
        address_dic_list = []
        for address in addresses:
            address_dic = {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "province_id": address.province.id,
                "city": address.city.name,
                "city_id": address.city.id,
                "district": address.district.name,
                "district_id": address.district.id,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }
            address_dic_list.append(address_dic)
        context = {
            # default_address_id?
            'default_address_id': login_user.default_address_id,
            'addresses': address_dic_list
        }
        return render(request=request, template_name='user_center_site.html', context=context)

    def post(self, request: HttpRequest):
        """实现新增地址逻辑"""
        # 判断是否超过地址上限：最多20个
        # Address.objects.filter(user=request.user).count()
        count = request.user.addresses.count()
        if count >= constants.USER_ADDRESS_COUNTS_LIMIT:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '超过地址数量上限'})

        # 接受参数
        json_dic = json.loads(request.body.decode())
        receiver = json_dic.get('receiver')
        province_id = json_dic.get('province_id')
        city_id = json_dic.get('city_id')
        district_id = json_dic.get('district_id')
        place = json_dic.get('place')
        mobile = json_dic.get('mobile')
        tel = json_dic.get('tel')
        email = json_dic.get('email')

        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('参数mobile错误')
        if tel:
            if not re.match(r"^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$", tel):
                return http.HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('参数email有误')

        # 保存地址信息
        try:
            address: Address = Address.objects.create(
                user=request.user,
                title=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )

            # 设置默认地址
            if not request.user.default_address:
                request.user.default_address = address
                request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '新增地址失败'})

        # 新增地址成功，将新增的地址响应给前端实现局部刷新
        address_dic = {
            'id': address.id,
            'title': address.title,
            'receiver': address.receiver,
            'province': address.province.name,
            'city': address.city.name,
            'district': address.district.name,
            'place': address.place,
            'mobile': address.mobile,
            'tel': address.tel,
            'email': address.email
        }
        return http.JsonResponse({'code': RETCODE.OK,
                                  'address': address_dic,
                                  'errmsg': '新增地址成功'})


class UpdateDestroyAddressView(LoginRequiredJSONMixin, View):
    """修改删除地址"""

    def put(self, request: HttpRequest, address_id: str):
        """修改地址"""

        # 接受参数
        json_dic = json.loads(request.body.decode())
        receiver = json_dic.get('receiver')
        province_id = json_dic.get('province_id')
        city_id = json_dic.get('city_id')
        district_id = json_dic.get('district_id')
        place = json_dic.get('place')
        mobile = json_dic.get('mobile')
        tel = json_dic.get('tel')
        email = json_dic.get('email')

        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('参数mobile错误')
        if tel:
            if not re.match(r"^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$", tel):
                return http.HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('参数email有误')

        # 判断是否存在，并更新地址
        try:
            Address.objects.filter(id=address_id).update(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '更新地址失败'})

        # 构造响应数据
        address = Address.objects.get(id=address_id)
        address_dic = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "province_id": address.province.id,
            "city": address.city.name,
            "city_id": address.city.id,
            "district": address.district.name,
            "district_id": address.district.id,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '更新地址成功', 'address': address_dic})

    def delete(self, request: HttpRequest, address_id: str):
        """删除地址"""
        try:
            address = Address.objects.get(id=address_id)
            address.is_delete = True
            address.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '删除地址失败'})

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除地址成功'})


class DefaultAddressView(LoginRequiredJSONMixin, View):
    """设置默认地址"""

    def put(self, request: HttpRequest, address_id: str):
        """设置默认地址"""
        try:
            default_address = Address.objects.get(id=address_id)
            request.user.default_address = default_address
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '设置默认地址失败'})
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '设置默认地址成功'})


class UpdateTitleAddressView(LoginRequiredJSONMixin, View):
    """设置地址标题"""

    def put(self, request: HttpRequest, address_id: str):
        json_dict: dict = json.loads(request.body.decode())
        title: str = json_dict.get('title')

        try:
            address = Address.objects.get(id=address_id)
            address.title = title
            address.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '设置地址标题失败'})
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '设置地址标题成功'})


class ChangePasswordView(LoginRequiredMixin, View):

    def get(self, request: HttpRequest):
        """展示修改密码界面"""
        return render(request, 'user_center_pass.html')

    def post(self, request: HttpRequest):
        """实现修改密码逻辑"""
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        new_password2 = request.POST.get('new_password2')

        if not all([old_password, new_password, new_password2]):
            return http.HttpResponseForbidden(content='缺少必传参数')

        # 检查用户密码
        try:
            request.user.check_password(old_password)
        except Exception as e:
            logger.error(e)
            return render(request, 'user_center_pass.html', {'origin_pwd_errmsg': '原始密码错误'})
        if not re.match(r'^[0-9A-Za-z]{8,20}$', new_password):
            return http.HttpResponseForbidden('密码最少8位，最长20位')
        if new_password != new_password2:
            return http.HttpResponseForbidden('两次输入的密码不一致')

        # 修改密码
        try:
            request.user.set_password(raw_password=new_password)
            request.user.save()
        except Exception as e:
            return render(request, 'user_center_pass.html', context={'change_pwd_errmsg': '修改密码失败'})

        # 清理状态保持信息
        logout(request)
        response = redirect(to=reverse('users:login'))
        response.delete_cookie(key='username')

        return response


class UserBrowseHistory(LoginRequiredJSONMixin, View):
    """用户浏览记录"""

    def post(self, request: HttpRequest):
        """保存用户浏览记录"""
        # 接受参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')

        # 校验参数
        try:
            models.SKU.objects.get(id=sku_id)
        except models.SKU.DoesNotExist:
            return http.HttpResponseForbidden(content='sku不存在')
        # 保存用户浏览数据
        redis_conn = get_redis_connection('history')
        pl = redis_conn.pipeline()
        user_id = request.user.id

        # 去重
        pl.lrem('history_%s' % user_id, 0, sku_id)
        # 添加
        pl.lpush('history_%s' % user_id, sku_id)
        # 截取
        pl.ltrim('history_%s' % user_id, 0, 4)
        # 执行
        pl.execute()

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})

    def get(self, request: HttpRequest):
        """获取用户浏览记录"""
        # 获取Redis存储的sku_id列表信息
        redis_conn = get_redis_connection(alias='history')
        user_id = request.user.id
        sku_ids = redis_conn.lrange('history_%s' % user_id, 0, -1)

        skus = []
        for sku_id in sku_ids:
            sku = models.SKU.objects.get(id=sku_id)
            skus.append({
                'id': sku.id,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price
            })
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'skus': skus})


class UserOrderInfoView(LoginRequiredMixin, View):
    """我的订单"""

    def get(self, request:HttpRequest, page_num:int):
        """提供我的订单页面"""

        user = request.user
        # 查询我的订单
        orders = user.orderinfo_set.all().order_by("-create_time")
        pass
