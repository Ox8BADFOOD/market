#!/usr/bin/env python
import os
import sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
if __name__ == '__main__':
    # 默认开发环境配置文件
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'market.settings.dev')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
