from .base import *

DEBUG = True

SECRET_KEY = os.environ['SECRET_KEY']


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'sirius',
        'USER': 'siriusadmin',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '',
    }
}

AWS_SES_REGION_NAME = os.environ['AWS_SES_REGION_NAME']
AWS_SES_REGION_ENDPOINT = os.environ['AWS_SES_REGION_ENDPOINT']
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = os.environ['DEFAULT_FROM_EMAIL']
SERVER_EMAIL = os.environ['SERVER_EMAIL']
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ['SERVER_EMAIL']
EMAIL_HOST_PASSWORD = os.environ['SIRIUS_EMAIL_PASS']


MEDIA_ROOT = os.environ['MEDIA_ROOT']

INTERNAL_IPS = '127.0.0.1'

INSTALLED_APPS += ['debug_toolbar', 'django_extensions', 'storages', 's3file']

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    's3file.middleware.S3FileMiddleware',
]


TEMPLATES[0]['DIRS'] = ['templates',]

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TEMPLATE_CONTEXT': True,
}

FIXTURE_DIRS = ['fixtures']

GRAPH_MODELS = {
    'all_applications': True,
    'group_models': True,
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.template': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
    },
}

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
AWS_LOCATION = 'media'
