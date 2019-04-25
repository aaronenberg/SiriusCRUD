import json
import logging
import os
from boto3.session import Session
from django.core.exceptions import ImproperlyConfigured
from .base import *


configs = {}
CONFIG_FILES = [
    'DB_CONFIG',
    'EMAIL_CONFIG',
    'SECRETS',
    'AWS_CONFIG'
]
for config in CONFIG_FILES:
    with open(os.environ.get(config)) as f:
        configs.update(json.loads(f.read()))

def get_env_var(setting, configs=configs):
     try:
         val = configs[setting]
         if val == 'True':
             val = True
         elif val == 'False':
             val = False
         return val
     except KeyError:
         error_msg = "ImproperlyConfigured: Set {0} environment variable".format(setting)
         raise ImproperlyConfigured(error_msg)

DEBUG = False

SECRET_KEY = get_env_var('SECRET_KEY')

INSTALLED_APPS += ['storages']

ALLOWED_HOSTS += ['.elasticbeanstalk.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': get_env_var('RDS_DB_NAME'),
        'USER': get_env_var('RDS_USERNAME'),
        'PASSWORD': get_env_var('RDS_PASSWORD'),
        'HOST': get_env_var('RDS_HOSTNAME'),
        'PORT': get_env_var('RDS_PORT'),
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = get_env_var('SERVER_EMAIL')
SERVER_EMAIL = get_env_var('SERVER_EMAIL')
EMAIL_HOST = get_env_var('EMAIL_HOST')
EMAIL_PORT = 587
EMAIL_HOST_USER = get_env_var('SERVER_EMAIL')
EMAIL_HOST_PASSWORD = get_env_var('SERVER_EMAIL_PASSWORD')


TEMPLATES[0]['DIRS'] = ['templates',]
FIXTURE_DIRS = ['fixtures']

AWS_ACCESS_KEY_ID = get_env_var('AWS_ACCESS_KEY_ID')
AWS_STORAGE_BUCKET_NAME = get_env_var('AWS_STORAGE_BUCKET_NAME')
AWS_SECRET_ACCESS_KEY = get_env_var('AWS_SECRET_ACCESS_KEY')
AWS_S3_REGION_NAME = get_env_var('AWS_S3_REGION_NAME')
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_S3_OBJECT_PARAMETERS = {
    'Expires': 'Thu, 31 Dec 2099 20:00:00 GMT',
    'CacheControl': 'max-age=94608000',
}

AWS_SES_REGION_NAME = 'us-west-2'
AWS_SES_REGION_ENDPOINT = 'email.us-west-2.amazonaws.com'

STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_LOCATION = 'static'
STATICFILES_STORAGE = 'config.custom_storages.StaticStorage'

MEDIAFILES_LOCATION = 'media'
DEFAULT_FILE_STORAGE = 'config.custom_storages.MediaStorage'

boto3_session = Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                        region_name='us-west-1')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        'level': logging.ERROR,
        'handlers': ['console'],
    },
    'formatters': {
        'simple': {
            'format': u"%(asctime)s [%(levelname)-8s] %(message)s",
            'datefmt': "%Y-%m-%d %H:%M:%S"
        },
        'aws': {
            # you can add specific format for aws here
            'format': u"%(asctime)s [%(levelname)-8s] %(message)s",
            'datefmt': "%Y-%m-%d %H:%M:%S"
        },
    },
    'handlers': {
        'watchtower': {
            'level': 'DEBUG',
            'class': 'watchtower.CloudWatchLogHandler',
                     'boto3_session': boto3_session,
                     'log_group': 'sirius-log',
                     'stream_name': 'sirius-log-stream',
            'formatter': 'aws',
        },
    },
    'loggers': {
        'django': {
            'level': 'INFO',
            'handlers': ['watchtower'],
            'propagate': False,
        },
        # add your other loggers here...
    },
}
