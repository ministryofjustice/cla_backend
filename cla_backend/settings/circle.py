import os
from .testing import *

ADMINS = (
    ('CLA', 'cla-alerts@digital.justice.gov.uk'),
)

MANAGERS = ADMINS

DATABASES['default']['NAME'] = os.environ.get('DB_NAME', 'circle_test')
DATABASES['default']['USER'] = os.environ.get('DB_USER', 'root')
DATABASES['default']['PASSWORD'] = os.environ.get('DB_PASSWORD', '')
DATABASES['default']['HOST'] = os.environ.get('DB_HOST', 'localhost')
DATABASES['default']['PORT'] = os.environ.get('DB_PORT', '')
