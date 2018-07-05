import os
from .testing import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('CLA', 'cla-alerts@digital.justice.gov.uk'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DB_NAME', 'cla_backend'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', ''),
        'PORT': os.environ.get('DB_PORT', ''),
    }
}
<<<<<<< HEAD

JENKINS_TEST_RUNNER = 'core.testing.CLADiscoverRunner'
=======
>>>>>>> e2a346ad... Fix typo in Circle CI directory and filename

#HOST_NAME = ""


ALLOWED_HOSTS = [
    '*'
]
