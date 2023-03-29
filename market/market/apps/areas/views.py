from django import http
from django.core.cache import cache
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import QuerySet
from django.shortcuts import render
from django.views import View
from areas.models import Area
from django.db import models
import logging

from market.utils.response_code import RETCODE

logger = logging.getLogger('django')


class AreasView(View):
    """省市区数据"""

    def get(self, request: WSGIRequest):
        """提供省市区数据"""
        area_id: str = request.GET.get(key="area_id")
        # 如果无id就是查询省
        if not area_id:
            # 读取省份缓存数据
            province_json_list = cache.get('province_list')
            if not province_json_list:
                try:
                    # 查询省份数据
                    province_model_list: QuerySet[Area] = Area.objects.filter(parent__isnull=True)

                    # 序列化省级数据
                    province_json_list = []
                    for province_model in province_model_list:
                        province_dic: dict = {'id': province_model.id, 'name': province_model.name }
                        province_json_list.append(province_dic)

                    # 存储省份缓存数据
                    cache.set('province_list', province_json_list, 3600)
                except Exception as e:
                    logger.error(e)
                    return http.JsonResponse(data={'code': RETCODE.DBERR, 'errmsg': '省份数据错误'})

            return http.JsonResponse(data={
                'code': RETCODE.OK,
                'errmsg': 'OK',
                'province_list': province_json_list
            })

        else:
            # 如果有id，就是查市或者区

            # 读取市或区缓存数据
            resp_data = cache.get('sub_area_' + area_id)
            if not resp_data:
                try:
                    # 拿到area_id节点
                    parent_model = Area.objects.get(id=area_id)
                    sub_model_list = parent_model.subs.all()

                    # 序列化
                    sub_json_list = []
                    for sub_model in sub_model_list:
                        sub_json_list.append({
                            'id': sub_model.id,
                            'name': sub_model.name
                        })
                    resp_data = {
                        # 父级id
                        'id': parent_model.id,
                        # 父级name
                        'name': parent_model.name,
                        # 父级包含的子集
                        'subs': sub_json_list
                    }
                    # 储存市或区缓存数据
                    cache.set('sub_area_' + area_id, resp_data, 3600)
                except Exception as e:
                    logger.error(e)
                    http.JsonResponse(data={
                        'code': RETCODE.DBERR,
                        'errmsg': '城市或区错误'
                    })

            return http.JsonResponse(data={
                'code': RETCODE.OK,
                'errmsg': 'OK',
                'sub_data': resp_data
            })
