import os
import json
from django.core.exceptions import ImproperlyConfigured
from .base import *


with open(os.environ.get('CONFIG_SECRETS')) as f:
 secrets = json.loads(f.read())

def get_env_var(setting, secrets=secrets):
     try:
         val = secrets[setting]
         if val == 'True':
             val = True
         elif val == 'False':
             val = False
         return val
     except KeyError:
         error_msg = "ImproperlyConfigured: Set {0} environment variable".format(setting)
         raise ImproperlyConfigured(error_msg)

DEBUG = False

SECRET_KEY = get_env_var('SIRIUS_SECRET_KEY')

ALLOWED_HOSTS += ['']

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
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = get_env_var('SERVER_EMAIL')
EMAIL_HOST_PASSWORD = get_env_var('SERVER_EMAIL_PASSWORD')


MEDIA_ROOT = get_env_var('SIRIUS_MEDIA_ROOT')

TEMPLATES[0]['DIRS'] = ['templates',]
