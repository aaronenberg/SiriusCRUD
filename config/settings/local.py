from .base import *

DEBUG = True

SECRET_KEY = os.environ['SIRIUS_SECRET_KEY']

ALLOWED_HOSTS += ['*']

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

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = os.environ['EMAIL']
SERVER_EMAIL = os.environ['EMAIL']
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ['EMAIL']
EMAIL_HOST_PASSWORD = os.environ['SIRIUS_EMAIL_PASS']


MEDIA_ROOT = os.environ['SIRIUS_MEDIA_ROOT']

INTERNAL_IPS = '127.0.0.1'

INSTALLED_APPS += ['debug_toolbar', ]

MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware',]

TEMPLATES[0]['DIRS'] = ['templates',]

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TEMPLATE_CONTEXT': True,
}

FIXTURE_DIRS = ['fixtures']
