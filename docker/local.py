from .base import *
import os

SECRET_KEY = os.environ["SECRET_KEY"]

DEBUG = bool(os.environ.get('DEBUG', False))

ALLOWED_HOSTS = os.environ['ALLOWED_HOSTS'].split(',')

TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Marco Fucci', 'marco.fucci@digital.justice.co.uk'),
    ('Rai Kotecha', 'ravi.kotecha@digital.justice.gov.uk'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'cla_backend',
        'USER': 'www-data',
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', ''),                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}

RAVEN_CONFIG = {
    'dsn': os.environ.get('RAVEN_CONFIG', 'https://298cb46e45fd412ebb49ac1f243db641:21c7e1c2d56b43d093737de1f7cc3019@app.getsentry.com/23077'),
}

INSTALLED_APPS += (
    'raven.contrib.django.raven_compat',
)

#HOST_NAME = "http://"
