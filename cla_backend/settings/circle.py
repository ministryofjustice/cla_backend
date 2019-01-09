import os
from .testing import *

ADMINS = (("CLA", "cla-alerts@digital.justice.gov.uk"),)

MANAGERS = ADMINS

DATABASES = {
    "default": {
        "ENGINE": "cla_backend.apps.reports.db.backend",
        "NAME": os.environ.get("DB_NAME", "circle_test"),
        "USER": os.environ.get("DB_USER", "root"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", ""),
    }
}
