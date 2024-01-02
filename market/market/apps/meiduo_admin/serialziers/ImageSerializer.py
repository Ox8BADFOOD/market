from django.conf import settings
from fdfs_client.client import Fdfs_client
from rest_framework import serializers
from rest_framework.response import Response

from celery_tasks.static_file.task import get_detail_html
from goods.models import SKUImage


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKUImage
        fields = '__all__'

    def create(self, validated_data):
        # 创建FastDFS连接对象
        client = Fdfs_client(settings.FASTDFS_PATH)
        # 获取前端传递的image文件
        data = self.context['request'].FILES.get('image')
        # 上传图片到fastDFS
        res = client.upload_by_buffer(data.read())
        # 判断是否上传成功
        if res['Status'] != 'Upload successed.':
            return Response(status=403)
        # 获取上传后的路径
        image_url = res['Remote file_id']
        # 获取sku_id
        sku_id = self.context['request'].data.get('sku')[0]
        # 生成新的详情页面
        get_detail_html.delay(sku_id=sku_id)
        # 保存图片
        img = SKUImage.objects.create(sku_id=sku_id, image=image_url)
        return img

    def update(self, instance: SKUImage, validated_data):
        # 创建FastDFS连接对象
        client = Fdfs_client(settings.FASTDFS_PATH)
        # 获取前端传递的image文件
        data = self.context['request'].FILES.get('image')
        # 上传图片到fastDFS
        res = client.upload_by_buffer(data.read())
        # 判断是否上传成功
        if res['Status'] != 'Upload successed.':
            return Response(status=403)
        # 获取上传后的路径
        image_url = res['Remote file_id']
        # 生成新的详情页面
        get_detail_html.delay(sku_id=instance.sku_id)
        # 保存图片
        instance.image = image_url
        # 数据库保存
        instance.save()
        return instance
