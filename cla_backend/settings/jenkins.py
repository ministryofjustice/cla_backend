import os
from .testing import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('CLA', 'cla-alerts@digital.justice.gov.uk'),
)

MANAGERS = ADMINS

INSTALLED_APPS += ('django_jenkins',)

JENKINS_TASKS = (
    'django_jenkins.tasks.with_coverage',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'cla_backend',
        'TEST_NAME': 'test_cla_backend%s' % (os.environ.get('BACKEND_BASE_PORT', '')),  # WARNING: if you want to change this, you NEED to change the dropdb arg in frontend build.py as well
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}

#JENKINS_TEST_RUNNER = 'core.test_runners.AdvancedCITestSuiteRunner'

#HOST_NAME = ""


ALLOWED_HOSTS = [
    '*'
]
