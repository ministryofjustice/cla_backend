import os
from .testing import *
from .testing import LOGGING

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

TEST_OUTPUT_DIR = "test-reports"

LOGGING["handlers"]["console"]["level"] = "WARN"

CFE_URL = "https://main-cfe-civil-uat.cloud-platform.service.justice.gov.uk/v6/assessments"
