from .testing import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Marco Fucci', 'marco.fucci@digital.justice.co.uk'),
    ('Rai Kotecha', 'ravi.kotecha@digital.justice.gov.uk'),
)

MANAGERS = ADMINS

INSTALLED_APPS += ('django_jenkins',)

JENKINS_TASKS = (
    'django_jenkins.tasks.with_coverage',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'jenkins_test',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}

#JENKINS_TEST_RUNNER = 'core.test_runners.AdvancedCITestSuiteRunner'

#HOST_NAME = ""
