from .base import *

DEBUG = False

SECRET_KEY = os.environ['SIRIUS_SECRET_KEY']

ALLOWED_HOSTS += ['']

if 'RDS_HOSTNAME' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.environ['RDS_DB_NAME'],
            'USER': os.environ['RDS_USERNAME'],
            'PASSWORD': os.environ['RDS_PASSWORD'],
            'HOST': os.environ['RDS_HOSTNAME'],
            'PORT': os.environ['RDS_PORT'],
        }
    }

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = os.environ['EMAIL']
SERVER_EMAIL = os.environ['EMAIL']
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ['EMAIL']
EMAIL_HOST_PASSWORD = os.environ['SIRIUS_EMAIL_PASS']


MEDIA_ROOT = os.environ['SIRIUS_MEDIA_ROOT']

TEMPLATES[0]['DIRS'] = ['templates',]
