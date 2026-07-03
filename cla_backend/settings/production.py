from .base import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (("MoJ", "Your email"),)

MANAGERS = ADMINS


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "cla_backend",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    }
}
