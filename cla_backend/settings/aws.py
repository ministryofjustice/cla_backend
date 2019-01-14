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

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ.get("DB_USERNAME", ""),
        "TEST_NAME": "test_cla_backend%s" % os.environ.get("BACKEND_TEST_DB_SUFFIX", ""),
        "USER": os.environ.get("DB_USERNAME", ""),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", ""),
        "PORT": os.environ.get("DB_PORT", ""),
    }
}

if os.environ.get("REPLICA_DB_HOST", ""):
    DATABASES["reports"] = {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ.get("DB_USERNAME", ""),
        "USER": os.environ.get("DB_USERNAME", ""),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("REPLICA_DB_HOST", ""),
        "PORT": os.environ.get("DB_PORT", ""),
    }
