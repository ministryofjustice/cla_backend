import datetime
import sys
import os

import sentry_sdk
from boto.s3.connection import NoHostProvided
from cla_common.call_centre_availability import OpeningHours
from cla_common.services import CacheAdapter
from collections import defaultdict
from kombu import transport
from sentry_sdk.integrations.django import DjangoIntegration

from cla_backend.sqs import CLASQSChannel


def env_var_truthy_intention(name):
    '''Returns True if the env var is truthy and not the string "False"'''
    value = os.environ.get(name, False)
    return value and value != "False"


# PATH vars

here = lambda *x: os.path.join(os.path.abspath(os.path.dirname(__file__)), *x)
PROJECT_ROOT = here("..")
root = lambda *x: os.path.join(os.path.abspath(PROJECT_ROOT), *x)

sys.path.insert(0, root("apps"))
sys.path.insert(0, root("libs"))

SHOW_NEW_CB1 = os.environ.get("SHOW_NEW_CB1", "False").lower() == "true"

HEALTHCHECKS = ["moj_irat.healthchecks.database_healthcheck", "status.healthchecks.check_disk"]

AUTODISCOVER_HEALTHCHECKS = True

PING_JSON_KEYS = {
    "build_date_key": "APP_BUILD_DATE",
    "commit_id_key": "APP_GIT_COMMIT",
    "version_number_key": "APPVERSION",
    "build_tag_key": "APP_BUILD_TAG",
}

DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
TEMPLATE_DEBUG = DEBUG

ADMINS = ()

MANAGERS = ADMINS

EMAIL_FROM_ADDRESS = "no-reply@civillegaladvice.service.gov.uk"
DEFAULT_EMAIL_TO = "cla-alerts@digital.justice.gov.uk"


OPERATOR_USER_ALERT_EMAILS = []
SPECIALIST_USER_ALERT_EMAILS = []

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ.get("DB_NAME", "cla_backend"),
        "USER": os.environ.get("DB_USER", "postgres"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", ""),
        "PORT": os.environ.get("DB_PORT", ""),
    }
}

if os.environ.get("REPLICA_DB_HOST", ""):
    DATABASES["reports"] = {
        "ENGINE": "cla_backend.apps.reports.db.backend",
        "NAME": os.environ.get("DB_NAME", "cla_backend"),
        "USER": os.environ.get("DB_USER", "postgres"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("REPLICA_DB_HOST", ""),
        "PORT": os.environ.get("DB_PORT", ""),
    }
else:
    DATABASES["reports"] = {
        "ENGINE": "cla_backend.apps.reports.db.backend",
        "NAME": os.environ.get("DB_NAME", "cla_backend"),
        "USER": os.environ.get("DB_USER", "postgres"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", ""),
        "PORT": os.environ.get("DB_PORT", ""),
    }

TEMP_DIR = root("tmp")
EXPORT_DIR = "/exports/"


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
if os.environ.get("STATIC_FILES_BACKEND") == "s3":
    STATICFILES_STORAGE = "cla_backend.libs.aws.s3.StaticS3Storage"

AWS_S3_REGION_NAME = os.environ.get("AWS_S3_REGION_NAME", "eu-west-1")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_DEFAULT_ACL = None
AWS_QUERYSTRING_AUTH = False

# Annoyingly the host parameter boto.s3.connection.S3Connection needs to be host string if it's not the default
# value of boto.s3.connection.NoHostProvided class reference and not None
AWS_S3_HOST = os.environ.get("AWS_S3_HOST", NoHostProvided)

# This bucket needs to a private bucket as it will contain sensitive reports
AWS_REPORTS_STORAGE_BUCKET_NAME = os.environ.get("AWS_REPORTS_STORAGE_BUCKET_NAME")
# This bucket needs to a public bucket as it will serve public assets such as css,images and js
AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STATIC_FILES_STORAGE_BUCKET_NAME")

AWS_DELETED_OBJECTS_BUCKET_NAME = os.environ.get("AWS_DELETED_OBJECTS_BUCKET_NAME")

SITE_HOSTNAME = os.environ.get("SITE_HOSTNAME", "cla.local:8000")

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split()

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = "Europe/London"

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "en-gb"
LANGUAGES = (("en-gb", "English"), ("cy", "Cymraeg"))
LOCALE_PATHS = (root("translations"),)

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = root("assets", "uploads")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = "/media/"

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = root("static")

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = "/static/"

# Additional locations of static files
STATICFILES_DIRS = (root("assets"),)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = os.environ.get("SECRET_KEY", "iia425u_J_pwntnEyqBuI1xBDqOX8nZ4uC73epGce_w")

# List of callables that know how to import templates from various sources.
# TEMPLATE_LOADERS = (
#     'django.template.loaders.filesystem.Loader',
#     'django.template.loaders.app_directories.Loader',
# )

MIDDLEWARE_CLASSES = (
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "status.middleware.MaintenanceModeMiddleware",
)

ROOT_URLCONF = "cla_backend.urls"

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = "cla_backend.wsgi.application"

TEMPLATE_DIRS = (root("templates"),)

BACKEND_ENABLED = os.environ.get("BACKEND_ENABLED", "True") == "True"
ADMIN_ENABLED = os.environ.get("ADMIN_ENABLED", "True") == "True"
INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "djorm_pgfulltext",
)

PROJECT_APPS = (
    "core",
    "legalaid",
    "cla_butler",
    "cla_provider",
    "call_centre",
    "cla_eventlog",
    "knowledgebase",
    "timer",
    "diagnosis",
    "status",
    "historic",
    "cla_auth",
    "checker",
    "eligibility_calculator",
    "guidance",
    "notifications",
    "complaints",
    "cla_auditlog",
)

if BACKEND_ENABLED:
    INSTALLED_APPS += ("rest_framework", "oauth2_provider")
if ADMIN_ENABLED:
    INSTALLED_APPS += ("django.contrib.admin", "pagedown", "reports")

OAUTH2_PROVIDER_APPLICATION_MODEL = 'oauth2_provider.Application'

INSTALLED_APPS += PROJECT_APPS

# DIAGNOSIS
DIAGNOSIS_FILE_NAME = "graph.graphml"
CHECKER_DIAGNOSIS_FILE_NAME = "checker-graph.graphml"
DIAGNOSES_USE_TEMPLATES = True

# Address of server to send notifications to frontend
FRONTEND_HOST_NAME = os.environ.get("FRONTEND_HOST_NAME", "http://127.0.0.1")
EXPRESS_SERVER_PORT = os.environ.get("EXPRESS_SERVER_PORT", 8005)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"},
        "simple": {"format": "%(levelname)s %(message)s"},
        "logstash": {"()": "logstash_formatter.LogstashFormatter"},
    },
    "filters": {
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
        "require_debug_true": {"()": "django.utils.log.RequireDebugTrue"},
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "console": {"level": "INFO", "class": "logging.StreamHandler", "formatter": "simple", "stream": sys.stdout},
    },
    "loggers": {
        "": {"handlers": ["console"], "level": "DEBUG", "propagate": True},
        "django.request": {"handlers": ["mail_admins"], "level": "ERROR", "propagate": True},
    },
}


LOW_SAMPLE_RATE_TRANSACTIONS = ["/status/", "/status", "/admin/", "/admin/login/"]


def traces_sampler(sampling_context):
    try:
        name = sampling_context["wsgi_environ"].get("PATH_INFO")
    except Exception:
        pass
    else:
        if name in LOW_SAMPLE_RATE_TRANSACTIONS:
            return 0.0001
    return 0.1


if "SENTRY_DSN" in os.environ:
    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_DSN"),
        integrations=[DjangoIntegration()],
        traces_sampler=traces_sampler,
        environment=os.environ.get("CLA_ENV", "unknown"),
    )

# SECURITY

LOGIN_FAILURE_LIMIT = 5
LOGIN_FAILURE_COOLOFF_TIME = 60  # in minutes

# Django rest-framework-auth
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("oauth2_provider.ext.rest_framework.OAuth2Authentication",),
    "DEFAULT_PERMISSION_CLASSES": ("core.permissions.AllowNone",),
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_THROTTLE_RATES": {"login": "10/sec"},
}

# the start number of the LAA reference, must be 7 digit number and must
# not clash with existing - generated references so we are starting at 3million
LAA_REFERENCE_SEED = 3000000
TEST_MODE = False

EMAIL_TIMEOUT = 10

if all([os.environ.get("SMTP_USER"), os.environ.get("SMTP_PASSWORD"), os.environ.get("SMTP_HOST")]):
    EMAIL_BACKEND = "cla_backend.apps.core.mail.backends.TimeoutEmailBackend"
    EMAIL_HOST = os.environ.get("SMTP_HOST")
    EMAIL_HOST_USER = os.environ.get("SMTP_USER")
    EMAIL_HOST_PASSWORD = os.environ.get("SMTP_PASSWORD")
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

CALL_CENTRE_NOTIFY_EMAIL_ADDRESS = os.environ.get("CALL_CENTRE_NOTIFY_EMAIL_ADDRESS", DEFAULT_EMAIL_TO)

# LGA-2236 Set rota hours start and end times using environment variables so can change without updating the code.
# Want to alter start and end times via environment variables.
# In case these are not set, default values are set here
DEFAULT_NON_ROTA_START_TIME_HR = 8
DEFAULT_NON_ROTA_END_TIME_HR = 17
DEFAULT_ED_START_TIME_HR = 9
DEFAULT_ED_END_TIME_HR = 17
DEFAULT_DISCRIM_START_TIME_HR = 8
DEFAULT_DISCRIM_END_TIME_HR = 18

NON_ROTA_START_TIME_HR = int(os.environ.get("NON_ROTA_START_TIME_HR", DEFAULT_NON_ROTA_START_TIME_HR))
NON_ROTA_END_TIME_HR = int(os.environ.get("NON_ROTA_END_TIME_HR", DEFAULT_NON_ROTA_END_TIME_HR))

EDUCATION_START_TIME_HR = int(os.environ.get("EDUCATION_START_TIME_HR", DEFAULT_ED_START_TIME_HR))
EDUCATION_END_TIME_HR = int(os.environ.get("EDUCATION_END_TIME_HR", DEFAULT_ED_END_TIME_HR))

DISCRIMINATION_START_TIME_HR = int(os.environ.get("DISCRIMINATION_START_TIME_HR", DEFAULT_DISCRIM_START_TIME_HR))
DISCRIMINATION_END_TIME_HR = int(os.environ.get("DISCRIMINATION_END_TIME_HR", DEFAULT_DISCRIM_END_TIME_HR))

NON_ROTA_HOURS = {"weekday": (datetime.time(NON_ROTA_START_TIME_HR, 0), datetime.time(NON_ROTA_END_TIME_HR, 0))}
EDUCATION_DAILY_HOURS = (datetime.time(EDUCATION_START_TIME_HR, 0), datetime.time(EDUCATION_END_TIME_HR, 0))
DISCRIMINATION_NON_ROTA_HOURS = {
    "weekday": (datetime.time(DISCRIMINATION_START_TIME_HR, 0), datetime.time(DISCRIMINATION_END_TIME_HR, 0))
}

EDUCATION_NON_ROTA_HOURS = {
    "monday": EDUCATION_DAILY_HOURS,
    "tuesday": EDUCATION_DAILY_HOURS,
    "wednesday": EDUCATION_DAILY_HOURS,
    "thursday": EDUCATION_DAILY_HOURS,
}

# If an unknown or empty is used to get from NON_ROTA_OPENING_HOURS then it will default to a basic NON_ROTA_HOURS
NON_ROTA_OPENING_HOURS = defaultdict(lambda: OpeningHours(**NON_ROTA_HOURS))

# If provider types have different opening hours they will need to be added here, with the category they service as the key.
NON_ROTA_OPENING_HOURS["discrimination"] = OpeningHours(**DISCRIMINATION_NON_ROTA_HOURS)
NON_ROTA_OPENING_HOURS["education"] = OpeningHours(**EDUCATION_NON_ROTA_HOURS)


OBIEE_IP_PERMISSIONS = ("*",)

OBIEE_EMAIL_TO = os.environ.get("OBIEE_EMAIL_TO", DEFAULT_EMAIL_TO)
OBIEE_ZIP_PASSWORD = os.environ.get("OBIEE_ZIP_PASSWORD")

# celery
if all([env_var_truthy_intention("SQS_ACCESS_KEY"), env_var_truthy_intention("SQS_SECRET_KEY")]):
    import urllib

    BROKER_URL = "sqs://{access_key}:{secret_key}@".format(
        access_key=urllib.quote(os.environ.get("SQS_ACCESS_KEY"), safe=""),
        secret_key=urllib.quote(os.environ.get("SQS_SECRET_KEY"), safe=""),
    )
else:
    # if no BROKER_URL specified then don't try to use celery
    # because it'll just cause errors
    CELERY_ALWAYS_EAGER = True

CLA_ENV = os.environ.get("CLA_ENV", "local")

BROKER_TRANSPORT_OPTIONS = {
    "polling_interval": 10,
    "region": os.environ.get("SQS_REGION", "eu-west-1"),
    "wait_time_seconds": 20,
}

if os.environ.get("CELERY_PREDEFINED_QUEUE_URL"):
    # Monkey patch the SQS transport channel to use our channel
    # This is to stop actions such as ListQueues being triggered
    # which we do not have on the cloud platform environments
    transport.SQS.Transport.Channel = CLASQSChannel

    predefined_queue_url = os.environ.get("CELERY_PREDEFINED_QUEUE_URL")
    CELERY_DEFAULT_QUEUE = predefined_queue_url.split("/")[-1]
    BROKER_TRANSPORT_OPTIONS["predefined_queue_url"] = predefined_queue_url
else:
    BROKER_TRANSPORT_OPTIONS["queue_name_prefix"] = "env-%(env)s-" % {"env": CLA_ENV}

CELERY_ACCEPT_CONTENT = ["yaml"]  # because json serializer doesn't support dates
CELERY_TASK_SERIALIZER = "yaml"  # for consistency
CELERY_RESULT_SERIALIZER = "yaml"  # as above but not actually used
CELERY_ENABLE_UTC = True  # I think this is the default now anyway
CELERY_RESULT_BACKEND = None  # SQS doesn't support it
CELERY_IGNORE_RESULT = True  # SQS doesn't support it
CELERY_MESSAGE_COMPRESSION = "gzip"  # got to look after the pennies
CELERY_DISABLE_RATE_LIMITS = True  # they don't work with SQS
CELERY_ENABLE_REMOTE_CONTROL = False  # doesn't work well under docker
CELERY_TIMEZONE = "UTC"
# apps with celery tasks
CELERY_IMPORTS = ["reports.tasks", "notifications.tasks"]

CONTRACT_2018_ENABLED = os.environ.get("CONTRACT_2018_ENABLED", "True") == "True"
PING_JSON_KEYS["CONTRACT_2018_ENABLED_key"] = "CONTRACT_2018_ENABLED"

mortgage_cap_removal_date = os.environ.get("MORTGAGE_CAP_REMOVAL_DATE", "2021-01-28 00:00")
MORTGAGE_CAP_REMOVAL_DATE = datetime.datetime.strptime(mortgage_cap_removal_date, "%Y-%m-%d %H:%M")


def bank_holidays_cache_adapter_factory():
    from django.core.cache import cache

    return cache


CacheAdapter.set_adapter_factory(bank_holidays_cache_adapter_factory)

MAINTENANCE_MODE = os.environ.get("MAINTENANCE_MODE", "False") == "True"

# .local.py overrides all the common settings.
try:
    from .local import *
except ImportError:
    pass

# importing test settings file if necessary (TODO chould be done better)
if len(sys.argv) > 1 and "test" == sys.argv[1]:
    from .testing import *
