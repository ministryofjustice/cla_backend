from datetime import date, time
from .base import *


DEBUG = False
TEMPLATE_DEBUG = DEBUG

TEST_APPS = ("django_pdb",)

TEST_MODE = True

OBIEE_ZIP_PASSWORD = "test"

REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["login"] = "10000000000/sec"

TEST_RUNNER = "core.testing.CLADiscoverRunner"

DATABASES["default"]["ENGINE"] = "cla_backend.apps.reports.db.backend"

ALLOWED_HOSTS = ["*"]

TEST_OUTPUT_DIR = "test-reports"


class DisableMigrations(object):
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return "notmigrations"


MIGRATION_MODULES = DisableMigrations()
