from django.db import models
from django.contrib.auth.models import AbstractUser
from market.utils.models import BaseModel

class User(AbstractUser):
    """自定义用户模型类"""
    mobile = models.CharField(max_length=11, unique=True, verbose_name="手机号")
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')
    default_address = models.ForeignKey(to='Address',
                                        related_name='users',
                                        null=True,
                                        blank=True,
                                        on_delete=models.SET_NULL,
                                        verbose_name='默认地址')

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class Address(BaseModel):
    """用户地址"""
    #  cascade 表示级联操作，就是说，如果主键表中被参考字段更新，外键表中也更新，主键表中的记录被删除，外键表中改行也相应删除
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='addresses', verbose_name='用户')
    title = models.CharField(max_length=20, verbose_name='地址名称', default='')
    receiver = models.CharField(max_length=20, verbose_name='收货人', default='')
    province = models.ForeignKey(to='areas.Area', on_delete=models.PROTECT, related_name='province_addresses', verbose_name='省', null=True)
    city = models.ForeignKey(to='areas.Area', on_delete=models.PROTECT, related_name='city_addresses', verbose_name='市', null=True)
    district = models.ForeignKey(to='areas.Area', on_delete=models.PROTECT, related_name='district_addresses', verbose_name='区', null=True)
    place = models.CharField(max_length=50, null=True, verbose_name='地址')
    mobile = models.CharField(max_length=11, null=True, verbose_name='手机')
    tel = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name='固定电话')
    email = models.CharField(max_length=30, null=True, blank=True, default='', verbose_name='电子邮箱')
    is_delete = models.BooleanField(default=False, verbose_name='逻辑删除')

    class Meta:
        db_table = 'tb_address'
        verbose_name = '用户地址'
        verbose_name_plural = verbose_name
        ordering = ['-update_time']
