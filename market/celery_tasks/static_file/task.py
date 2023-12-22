#!/usr/bin/env python

import os
from typing import List, Type, Dict, Tuple

from django.db.models import QuerySet

from contents.utils import get_categories
from goods.models import SPU, SKU, SKUSpecification, SPUSpecification, SpecificationOption
from goods.utils import get_breadcrumb
from django.shortcuts import render
from django.conf import settings


def get_detail_html(sku_id: int):
    sku = SKU.objects.get(id=sku_id)

    # 分类数据
    categories = get_categories()
    # 获取面包屑导航
    breadcrumb = get_breadcrumb(sku.category)
    # 获取spu
    spu: SPU = sku.spu
    # 查询所有sku
    skus: QuerySet[SKU] = spu.sku_set.order_by('id')

    # 生成 options_sku_dict
    '''
    {
        规格选项元组:sku_id
    }
    '''
    options_sku_dict: dict[tuple[Type[int], ...], int] = {}
    sku_instance: SKU
    for sku_instance in skus:
        # SKU所有规格
        sku_instance_specs: QuerySet[SKUSpecification] = sku_instance.specs.order_by('spec_id')
        # options_sku_dict的key
        option_key = []

        sku_instance_spec: SKUSpecification
        for sku_instance_spec in sku_instance_specs:
            option_key.append(sku_instance_spec.option_id)
        options_sku_dict[tuple(option_key)] = sku_instance.id

    # 当前SKU的规格键，用于后面的匹配
    current_sku_option_list: list[Type[int]] = []
    sku_specs = sku.specs.order_by('spec_id')
    for spec in sku_specs:
        current_sku_option_list.append(spec.option.id)

    # sku对应spu所有规格列表（返回给模版）
    spu_specs_list: list[SPUSpecification] = []

    # 获取SPU所有规格信息（例如：电脑商品的屏幕尺寸、颜色、内存），并且排序过顺序是固定
    spu_specs: QuerySet[SPUSpecification] = spu.specs.order_by('id')
    # 遍历当前spu所有的规格
    spu_spec: SPUSpecification  # spu规格（例如：电脑商品的屏幕尺寸、颜色、内存）
    for index, spu_spec in enumerate(spu_specs):
        # 规格选项列表
        option_list: list[SpecificationOption] = []
        # 规格所有选项，例如 13.3寸 15.4寸
        spu_spec_options: QuerySet[SpecificationOption] = spu_spec.options.all()
        # 遍历spu规格选项（例如 13.3寸）
        option: SpecificationOption
        for option in spu_spec_options:
            # 复制当前sku的规格键
            sku_option_temp: list[Type[int]] = current_sku_option_list[:]
            # *** 替换对应索引的元素的选项值。组成屏幕尺寸、颜色、内存的各种选项值
            sku_option_temp[index] = option.id
            # *** 为选项添加sku_id属性，用于在html中输出链接
            option.sku_id = options_sku_dict.get(tuple(sku_option_temp), 0)
            # 添加选项对象
            option_list.append(option)
        # *** 为规格对象添加选项列表
        spu_spec.option_list = option_list
        # 重新构造规格数据
        spu_specs_list.append(spu_spec)

    context = {
        'sku': sku,
        'categories': categories,
        'breadcrumb': breadcrumb,
        'category_id': sku.category_id,
        'spu': spu,
        'specs': spu_specs_list
    }
    response = render(None, 'detail.html', context)

    file_name = os.path.join(settings.BASE_DIR, 'static/detail/%d.html' % sku.id)
    # 写文件
    with open(file_name, 'w') as f1:
        f1.write(response.content.decode())
