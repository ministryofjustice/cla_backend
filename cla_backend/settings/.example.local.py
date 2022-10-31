from .base import *

DEBUG = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        }
    },
    "loggers": {"django.request": {"handlers": ["mail_admins"], "level": "ERROR", "propagate": True}},
}

# So there is a separate database connection for the reports.
# See cla_backend/apps/reports/db/backend/base.py
# Only need to override the default connection if running locally.
# If override both keys then reports fail with error database connection isn't set to UTC
DATABASES["default"] = {
    "ENGINE": "django.db.backends.postgresql_psycopg2",
    "NAME": os.environ.get("DB_NAME", "cla_backend"),
    "USER": os.environ.get("DB_USER", "postgres"),
    "PASSWORD": os.environ.get("DB_PASSWORD", ""),
    "HOST": os.environ.get("DB_HOST", ""),
    "PORT": os.environ.get("DB_PORT", ""),
}

# don't bother with celery locally
CELERY_ALWAYS_EAGER = True

OBIEE_ZIP_PASSWORD = "test"
