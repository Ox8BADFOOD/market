from functools import wraps
from django import http
from django.contrib.auth.decorators import login_required
from market.utils.response_code import RETCODE, err_msg
from django.contrib.auth.mixins import LoginRequiredMixin

class LoginRequiredMixin(object):
    """
    使用多继承的MRO(方法解析顺序)特征。
    验证用户是否登录扩展类
    """

    @classmethod
    def as_view(cls, **initkwargs):

        # 自定义的as_view()方法中，调用父类的as_view()方法
        view = super().as_view(**initkwargs)
        return login_required(view)


class LoginRequiredJSONMixin(object):
    """验证用户是否登陆并返回json的扩展类"""

    @classmethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        return login_required_json(view)


def login_required_json(view_func):
    """
    判断用户是否登录的装饰器，并返回json
    :param view_func: 被装饰的视图函数
    :return: json、view_func
    """
    # 恢复view_func的名字和文档
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return http.JsonResponse({
                'code': RETCODE.SESSIONERR,
                'errmsg': err_msg[RETCODE.SESSIONERR]
                })
        else:
            return view_func(request, *args, **kwargs)
    return wrapper
