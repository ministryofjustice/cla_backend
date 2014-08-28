import os
from .testing import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Marco Fucci', 'marco.fucci@digital.justice.co.uk'),
    ('Ravi Kotecha', 'ravi.kotecha@digital.justice.gov.uk'),
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
        'TEST_NAME': 'cla_backend%s' % (os.environ.get('BACKEND_BASE_PORT', '')),
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
