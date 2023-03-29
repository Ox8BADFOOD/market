from django import http
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from verifications import constants
from verifications.libs.captcha.captcha import captcha


class ImageCodeView(View):
    """图形验证码"""

    def get(self, request, uuid):
        """
        :param request: 请求对象
        :param uuid: 唯一标识图形验证码所属于的用户
        :return: image/jpg
        """
        # 生成图片验证码
        text, image = captcha.generate_captcha()

        # 保存图片验证码
        redis_conn = get_redis_connection('verify_code')
        # 'img_%s' % uuid, constants.IMAGE_CODE_REDIS_EXPIRES, text)
        redis_conn.setex(name='img_%s' % uuid, time=constants.IMAGE_CODE_REDIS_EXPIRES, value=text)
        # 响应图片验证码
        return http.HttpResponse(image, content_type='image/jpg')
