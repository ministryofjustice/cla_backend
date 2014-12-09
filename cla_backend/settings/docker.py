from .base import *
import os

SECRET_KEY = os.environ["SECRET_KEY"]

DEBUG = True if os.environ.get('SET_DEBUG') == 'True' else False

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

#HOST_NAME = "http://"

# LOGGING CONFIG FOR DOCKER ENV
LOGGING['handlers']['production_file'] = {
    'level' : 'INFO',
    'class' : 'logging.handlers.RotatingFileHandler',
    'filename' : '/var/log/wsgi/app.log',
    'maxBytes': 1024*1024*5, # 5 MB
    'backupCount' : 7,
    'formatter': 'logstash',
    'filters': ['require_debug_false'],
}

LOGGING['handlers']['debug_file'] = {
    'level' : 'DEBUG',
    'class' : 'logging.handlers.RotatingFileHandler',
    'filename' : '/var/log/wsgi/debug.log',
    'maxBytes': 1024*1024*5, # 5 MB
    'backupCount' : 7,
    'formatter': 'verbose',
    'filters': ['require_debug_true'],
}

LOGGING['loggers'][''] = {
    'handlers': ['production_file', 'debug_file'],
    'level': "DEBUG",
}
