import os
import json
from django.core.exceptions import ImproperlyConfigured
from .base import *


configs = {}
CONFIG_FILES = ['SECRETS', 'DB_CONFIG', 'EMAIL_CONFIG', 'PATHS_CONFIG', 'ALLOWED_HOSTS']
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

ALLOWED_HOSTS += list(get_env_var('ALLOWED_HOSTS'))

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

MEDIA_ROOT = get_env_var('MEDIA_ROOT')

TEMPLATES[0]['DIRS'] = ['templates',]
FIXTURE_DIRS = ['fixtures']
