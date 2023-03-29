import re
from django.contrib.auth.backends import ModelBackend
from django.conf import settings
from .models import User
from itsdangerous import TimedJSONWebSignatureSerializer  as Serializer
from itsdangerous import BadData
from . import constants

def get_user_by_account(account):
    """
    根据account查询用户
    :param account: 用户名或者手机号
    :return: user
    """
    try:
        if re.match(r"^1[3-9]\d{9}$", account):
            # 登录手机号
            user = User.objects.get(mobile=account)
        else:
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    else:
        return user


class UsernameMobileAuthBackend(ModelBackend):
    """自定义用户认证后端"""


    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        重写认证方法，实现多账号登录
        :param request: 请求对象
        :param username: 用户名
        :param password: 密码
        :param kwargs: 其他参数
        :return: user
        """
        # 根据传入的username获取user对象。username可以是手机号也可以是账号
        user: User = get_user_by_account(username)
        # 校验user是否存在并校验密码是否正确
        if user and user.check_password(password):
            return user


def generate_verify_email_url(user):
    """
    生成邮箱验证链接: host + /emails/verification/ + '?token=' + token.decode()
    :param user: 当前登录用户
    :return: 验证邮箱的链接
    """
    serializer = Serializer(secret_key=settings.SECRET_KEY, expires_in=constants.VERIFY_EMAIL_TOKEN_EXPIRES)
    data = {'user_id': user.id, 'email': user.email}
    token = serializer.dumps(obj=data).decode()
    return settings.EMAIL_VERIFY_URL + '?token=' + token


def check_verify_email_token(token):
    """
    根据token获取user
    :param token:序列化后的用户信息
    :return:user
    """
    serializer = Serializer(secret_key=settings.SECRET_KEY, expires_in=constants.VERIFY_EMAIL_TOKEN_EXPIRES)
    try:
        data = serializer.loads(token)
    except BadData:
        return None
    else:
        user_id = data.get('user_id')
        email = data.get('email')
        try:
            user = User.objects.get(id=user_id, email=email)
        except User.DoesNotExist:
            return None
        else:
            return user
