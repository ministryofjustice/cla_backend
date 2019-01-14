from .base import *
import os

try:
    SECRET_KEY = os.environ["SECRET_KEY"]
except KeyError as e:
    print(
        "Secret key not found, using a default key for the docker build step only, "
        "please set the SECRET_KEY in your environment"
    )
    SECRET_KEY = "CHANGE_ME"
    pass

DEBUG = True if os.environ.get("SET_DEBUG") == "True" else False

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost").split(",")

TEMPLATE_DEBUG = DEBUG

ADMINS = (("CLA", "cla-alerts@digital.justice.gov.uk"),)

MANAGERS = ADMINS

LOGGING["loggers"][""] = {"handlers": ["console", "sentry"], "level": "DEBUG"}
