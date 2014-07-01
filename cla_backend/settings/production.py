from .base import *


DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('MoJ', 'Your email'),
)

MANAGERS = ADMINS


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'cla_backend',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

RAVEN_CONFIG = {
    'dsn': 'https://4f950e08988c4cfeba8e5b9cb82d1233:a60f0407af98435aa86fbca234992c74@app.getsentry.com/26717',
}

INSTALLED_APPS = INSTALLED_APPS + (
    'raven.contrib.django.raven_compat',
)
