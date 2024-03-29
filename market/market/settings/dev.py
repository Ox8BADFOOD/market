"""
Django settings for market project.

Generated by 'django-admin startproject' using Django 2.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""
import datetime
import os, sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
current_file_path = os.path.abspath(__file__)
BASE_DIR = os.path.dirname(os.path.dirname(current_file_path))
path = os.path.join(BASE_DIR, "apps")
print("path:%s" % (path))
sys.path.insert(0, path)

print(sys.path)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'v+kbc4@$lk@gdas#$2vlt2-q=k@kmae%o@2x+ag-jz(pvt&=-='

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# CORS 白名单
# Previously this setting was called CORS_ORIGIN_WHITELIST,
# which still works as an alias, with the new name taking precedence.
CORS_ORIGIN_WHITELIST = (
    'http://127.0.0.1:8080',
    'http://127.0.0.1:8000',
    'http://localhost:8080',
    'http://www.meiduo.site:8080',
    'http://api.meiduo.site:8000'
)

CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8080',
    'http://127.0.0.1:8000',
    'http://localhost:8080',
    'http://www.meiduo.site:8080',
    'http://api.meiduo.site:8000'
]

# 允许携带cookie
CORS_ALLOW_CREDENTIALS = True

# Application definition
INSTALLED_APPS = [
    # 全文检索
    'haystack',
    # 用户模块
    'users.apps.UsersConfig',
    'contents.apps.ContentsConfig',
    'verifications.apps.VerificationsConfig',
    'areas.apps.AreasConfig',
    'goods.apps.GoodsConfig',
    'carts.apps.CartsConfig',
    'orders.apps.OrdersConfig',
    'meiduo_admin.apps.MeiduoAdminConfig',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    # 跨域中间件
    'corsheaders.middleware.CorsMiddleware',
    # 支持中文语言
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'market.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            # 补充Jinja2模板引擎环境
            'environment': 'market.utils.jinja2_env.jinja2_environment',
        },
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    }
]

WSGI_APPLICATION = 'market.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '127.0.0.1',  # 数据库主机
        'PORT': 3306,  # 数据库端口
        'USER': 'Max',  # 数据库用户名
        'PASSWORD': 'qwer1234',  # 数据库用户密码
        'NAME': 'market',
    }
}

# redis
CACHES = {
    "default": {  # 默认
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "session": {  # session
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "verify_code": {  # 图形验证码
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "history": {  # 用户浏览记录
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/3",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "carts": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/4",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "session"

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# login
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # 是否禁用已经存在的日志器
    'formatters': {  # 日志信息显示的格式
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(lineno)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(module)s %(lineno)d %(message)s'
        },
    },
    'filters': {  # 对日志进行过滤
        'require_debug_true': {  # django在debug模式下才输出日志
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {  # 日志处理方法
        'console': {  # 向终端中输出日志
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {  # 向文件中输出日志
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            # 日志文件的位置
            'filename': os.path.join(os.path.dirname(BASE_DIR), 'logs/logs.log'),
            'maxBytes': 300 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose'
        },
    },
    'loggers': {  # 日志器
        'django': {  # 定义了一个名为django的日志器
            'handlers': ['console', 'file'],  # 可以同时向终端与文件中输出日志
            'propagate': True,  # 是否继续传递日志信息
            'level': 'INFO',  # 日志器接收的最低日志级别
        },
    }
}

LOGIN_URL = '/login/'

# 用户认证
AUTHENTICATION_BACKENDS = ["users.utils.UsernameMobileAuthBackend"]

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
STATIC_URL = '/static/'
# 配置静态文件加载路径
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

AUTH_USER_MODEL = "users.User"

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # 指定邮件后端
EMAIL_HOST = 'smtp.163.com'  # 发邮件主机
EMAIL_PORT = 25  # 发邮件端口
EMAIL_HOST_USER = 'bymiracles@163.com'  # 授权的邮箱
EMAIL_HOST_PASSWORD = 'EGDNTWMILUBHPLGL'  # 邮箱授权时获得的密码，非注册登录密码
EMAIL_FROM = '母爱妈妈<bymiracles@163.com>'  # 发件人抬头
EMAIL_VERIFY_URL = 'http://127.0.0.1:8000/emails/verification/'
# 指定自定义的Django文件存储类
# DEFAULT_FILE_STORAGE = 'market.utils.fastdfs.fdfs_storage.FastDFSStorage'
# FastDFS相关参数
MEDIA_URL = 'http://172.16.104.3:8888/'

# Haystack
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://172.16.104.3:9200/',  # Elasticsearch服务器ip地址，端口号固定为9200
        'INDEX_NAME': 'market',  # Elasticsearch建立的索引库的名称
    },
}

# 当添加、修改、删除数据时，自动生成索引
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

# FastDFS相关参数
FDFS_BASE_URL = 'http://172.16.104.3:8888/'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 使用rest_framework_simplejwt(token)验证身份
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        # 基于用户名密码认证方式
        'rest_framework.authentication.SessionAuthentication',
        # 基于Session认证方式
        'rest_framework.authentication.BasicAuthentication',
    ),
    # 'DEFAULT_PERMISSION_CLASSES': [
    #     'rest_framework.permissions.IsAuthenticated'  # 默认权限为验证用户
    # ],
}

# 指明token的有效期
SIMPLE_JWT = {
    # Access Token的有效期
    "ACCESS_TOKEN_LIFETIME": datetime.timedelta(days=5),
    # Refresh Token的有效期
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(days=1),
    # 是否自动刷新Refresh Token
    'ROTATE_REFRESH_TOKENS': False,
    # 刷新Refresh Token时是否将旧Token加入黑名单，如果设置为False，则旧的刷新令牌仍然可以用于获取新的访问令牌。
    # 需要将'rest_framework_simplejwt.token_blacklist'加入到'INSTALLED_APPS'的配置中
    'BLACKLIST_AFTER_ROTATION': False,
    # 加密算法
    'ALGORITHM': 'HS256',  # 加密算法
    # 签名密匙，这里使用Django的SECRET_KEY
    'SIGNING_KEY': SECRET_KEY,
    # 如为True，则在每次使用访问令牌进行身份验证时，更新用户最后登录时间
    "UPDATE_LAST_LOGIN": False,
    # 用于验证JWT签名的密钥返回的内容。可以是字符串形式的密钥，也可以是一个字典。
    "VERIFYING_KEY": "",
    # JWT中的"Audience"声明,用于指定该JWT的预期接收者。
    "AUDIENCE": None,
    # JWT中的"Issuer"声明，用于指定该JWT的发行者。
    "ISSUER": None,
    # 用于序列化JWT负载的JSON编码器。默认为Django的JSON编码器。
    "JSON_ENCODER": None,
    # 包含公钥的URL，用于验证JWT签名。
    "JWK_URL": None,
    # 允许的时钟偏差量，以秒为单位。用于在验证JWT的过期时间和生效时间时考虑时钟偏差。
    "LEEWAY": 0,
    # 用于指定JWT在HTTP请求头中使用的身份验证方案。默认为"Bearer"
    "AUTH_HEADER_TYPES": ("Bearer",),
    # 包含JWT的HTTP请求头的名称。默认为"HTTP_AUTHORIZATION"
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    # 用户模型中用作用户ID的字段。默认为"id"。
    "USER_ID_FIELD": "id",
    # JWT负载中包含用户ID的声明。默认为"user_id"。
    "USER_ID_CLAIM": "user_id",
    # 用于指定用户身份验证规则的函数或方法。默认使用Django的默认身份验证方法进行身份验证。
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    # 用于指定可以使用的令牌类。默认为"rest_framework_simplejwt.tokens.AccessToken"。
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    # JWT负载中包含令牌类型的声明。默认为"token_type"。
    "TOKEN_TYPE_CLAIM": "token_type",
    # 用于指定可以使用的用户模型类。默认为"rest_framework_simplejwt.models.TokenUser"。
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    # JWT负载中包含JWT ID的声明。默认为"jti"。
    "JTI_CLAIM": "jti",
    # 在使用滑动令牌时，JWT负载中包含刷新令牌过期时间的声明。默认为"refresh_exp"。
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    # 滑动令牌的生命周期。默认为5分钟。
    "SLIDING_TOKEN_LIFETIME": datetime.timedelta(minutes=5),
    # 滑动令牌可以用于刷新的时间段。默认为1天。
    "SLIDING_TOKEN_REFRESH_LIFETIME": datetime.timedelta(days=1),
    # 用于生成访问令牌和刷新令牌的序列化器。
    "TOKEN_OBTAIN_SERIALIZER": "meiduo_admin.serialziers.token.MyTokenObtainPairSerializer",
    # 用于刷新访问令牌的序列化器。默认
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    # 用于验证令牌的序列化器。
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    # 用于列出或撤销已失效JWT的序列化器。
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    # 用于生成滑动令牌的序列化器。
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
    # 用于刷新滑动令牌的序列化器。
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",
}

FASTDFS_PATH = os.path.join(BASE_DIR, 'utils/fastdfs/client.conf')
