from datetime import time
from .base import *  # noqa: F403

DEBUG = False
TEMPLATE_DEBUG = DEBUG

TEST_APPS = ("django_pdb",)

TEST_MODE = True

OBIEE_ZIP_PASSWORD = "test"

REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["login"] = "10000000000/sec"  # noqa: F405

TEST_RUNNER = "core.testing.CLADiscoverRunner"

DATABASES["default"]["ENGINE"] = "cla_backend.apps.reports.db.backend"  # noqa: F405

ALLOWED_HOSTS = ["*"]

TEST_OUTPUT_DIR = "test-reports"

OPERATOR_HOURS = {"weekday": (time(9, 0), time(20, 0)), "saturday": (time(9, 0), time(12, 30))}


class DisableMigrations(object):
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()

SESSION_SECURITY_WARN_AFTER = 5
SESSION_SECURITY_EXPIRE_AFTER = 10

ALWAYS_SUGGEST_PROVIDER = False
