from celery import Celery

# 为celery使用django配置文件进行设置
import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'market.settings.dev'

# 创建celery实例
celery_app = Celery('market')

# 加载celery配置
celery_app.config_from_object(obj='celery_tasks.config')

# 自动注册celery任务
celery_app.autodiscover_tasks(packages=['celery_tasks.email', 'celery_tasks.static_file'])
