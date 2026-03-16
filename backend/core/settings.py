import os
from datetime import timedelta

from corsheaders.defaults import default_headers

from pathlib import Path
from decouple import config

from django.utils.translation import gettext_lazy as _


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-!veg9i@#$s5qm30!xjckgq#@(eq6j9q(el#^ml7l8ja!sspoy2'

DEBUG = True

ALLOWED_HOSTS = ['*']


INSTALLED_APPS = [
    # head libs
    'encryption',
    'modeltranslation',
    
    # built-in
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # libs
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'drf_spectacular',
    'django_password_validators',
    'django_password_validators.password_history',
    'django_prometheus',
    'django_filters',
    'tinymce',

    # apps
    'apps.account',
    'apps.application',
    'apps.license_template',
    "apps.document",
    'apps.decree',
    'apps.organization'
]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'axes.middleware.AxesMiddleware',
    "django.middleware.locale.LocaleMiddleware",

    #PrometheusAfterMiddleware should be the last middleware in the list
    'django_prometheus.middleware.PrometheusAfterMiddleware'
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "apps" / "templates"], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


DATABASES = {
    "default": {
        "ENGINE": config("SQL_ENGINE", "django.db.backends.sqlite3"),
        "NAME": config("SQL_DATABASE", BASE_DIR / "db.sqlite3"),
        "USER": config("SQL_USER", "user"),
        "PASSWORD": config("SQL_PASSWORD", "password"),
        "HOST": config("SQL_HOST", "localhost"),
        "PORT": config("SQL_PORT", "5432"),
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": config("CELERY_BROKER_URL", default="redis://redis:6379/0", cast=str),
    },
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    }
]

LANGUAGE_CODE = 'ru'

LANGUAGES = [
    ('ru', _('Русский')),
    ('ky', _('Кыргызский'))
]
LOCALE_PATHS = (os.path.join(BASE_DIR, "locale"),)

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


STATIC_ROOT = os.path.join(BASE_DIR, 'static-root')
STATIC_URL = '/static-root/'


MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"



CELERY_RESULT_BACKEND = 'redis://' + config('REDIS_HOST') + ':' + config('REDIS_PORT') + '/0'
CELERY_BROKER_URL = 'redis://' + config('REDIS_HOST') + ':' + config('REDIS_PORT') + '/0'
CELERY_ACCEPT_CONTENT = ["json",'application/msgpack']
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_RESULT_EXTENDED = True


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = default_headers + (
    "cache-control",
    "Access-Control-Allow-Headers",
    "Access-Control-Allow-Credentials",
)

CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS').split(',')

CORS_ORIGIN_WHITELIST = config('CORS_ORIGIN_WHITELIST').split(',')


REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'apps.organization.auth.OrganizationJWTAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.ScopedRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'forgot_password': '100/hour'
    }
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=100000),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=100000),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,

    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,

    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",

    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",

    "JTI_CLAIM": "jti",

    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),

    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",
}

AUTH_USER_MODEL = 'account.User'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_PASSWORD')

SPECTACULAR_SETTINGS = {
    "TITLE": "DTEK documentation",
    "VERSION": "0.0.1",
    "TAGS": [
        {"name": "Account", "description": "Операции с пользователями"},
        {"name": "Application", "description": "Работа с заявками"},
        {"name": "License", "description": "Выдача и управление лицензиями"},
    ],
    "SCHEMA_PATH_PREFIX": "/api/v[0-9]",
    "SCHEMA_PATH_PREFIX_TRIM": False,
    "COMPONENT_SPLIT_REQUEST": True,  # convert "string image" to "binary image"
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_SETTINGS": {
        "defaultModelExpandDepth": 3,
        "defaultModelRendering": "model",
        "filter": True,
        "showCommonExtensions": True,
        "persistAuthorization": True,
        "displayOperationId": True,
        "deepLinking": True,
        "docExpansion": "none",
    },
}


# AXES_IGNORE_PATTERNS = [
#     r'^admin/',   # отключаем проверку для всего админки
# ]
# AXES_FAILURE_LIMIT = 5
# AXES_COOLOFF_TIME = 3
# AXES_LOCK_OUT_AT_FAILURE = True

# LOGGING = {
#     'version': 1,
#     'formatters': {
#         'verbose': {
#             'format': '{asctime} - {levelname} - {module} - {message}',
#             'style': '{',
#         },
#         'simple': {
#             'format': '{message}\n',
#             'style': '{',
#         },
#     },
#     'filters': {
#         'require_debug_true': {
#             '()': 'django.utils.log.RequireDebugTrue',
#         }
#     },
#     'handlers': {
#         'console': {
#             'level': 'DEBUG',
#             'filters': ['require_debug_true'],
#             'class': 'logging.StreamHandler',
#             'formatter': 'simple'
#         }
#     },
#     'loggers': {
#         'django.db.backends': {
#             'level': 'DEBUG',
#             'handlers': ['console'],
#         },
#         'django.request': {
#             'handlers': ['console'],
#             'propagate': True,
#             'level': 'DEBUG',
#         }
#     }
# }

# INTEGRATION
WSDL_FILE_PATH_MINUST = os.path.join(BASE_DIR, "apps/integration/", "min.wsdl")
WSDL_FILE_PATH_GNS = os.path.join(BASE_DIR, "apps/integration/", "gns.wsdl")
