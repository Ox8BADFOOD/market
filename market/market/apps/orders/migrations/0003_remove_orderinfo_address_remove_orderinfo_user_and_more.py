# Generated by Django 4.1.4 on 2023-12-29 06:10

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0002_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="orderinfo",
            name="address",
        ),
        migrations.RemoveField(
            model_name="orderinfo",
            name="user",
        ),
        migrations.DeleteModel(
            name="OrderGoods",
        ),
        migrations.DeleteModel(
            name="OrderInfo",
        ),
    ]
