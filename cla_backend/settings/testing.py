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

next_year = date.today().year + 1

OPERATOR_HOURS = {
    "weekday": (time(9, 0), time(20, 0)),
    "saturday": (time(9, 0), time(12, 30)),
    "{}-12-24".format(next_year): (time(9, 0), time(17, 30)),
    "{}-12-31".format(next_year): (time(9, 0), time(17, 30)),
}


class DisableMigrations(object):
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return "notmigrations"


MIGRATION_MODULES = DisableMigrations()
