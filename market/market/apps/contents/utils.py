from collections import OrderedDict
from goods.models import GoodsChannel


def get_categories():
    """
    提供商品频道组信息
    :return {
        '组id': {
                // 频道/一级类别
                'channels':[],
                // 二级类别sub_cats嵌套三级类别
                "sub_cats": []
                }
    }
    """
    categories = OrderedDict()
    channels = GoodsChannel.objects.order_by('group_id', 'sequence')
    for channel in channels:
        group_id = channel.group_id
        if group_id not in categories:
            categories[group_id] = {'channels': [], "sub_cats": []}
        # 当前频道的类别
        cat1 = channel.category

        # 追加当前频道
        categories[group_id]['channels'].append({
            'id': cat1.id,
            'name': cat1.name,
            'url': channel.url
        })

        # 构建当前类别的子类别
        for cat2 in cat1.subs.all():
            cat2.sub_cats = []
            for cat3 in cat2.subs.all():
                cat2.sub_cats.append(cat3)
            categories[group_id]['sub_cats'].append(cat2)
    return categories