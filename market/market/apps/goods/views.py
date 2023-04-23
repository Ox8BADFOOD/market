from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render
from django.views import View


class ListView(View):
    """商品列表"""

    def get(self, request, category_id, page_num):
        """
        提供商品列表
        :param request:
        :return:
        """
        pass