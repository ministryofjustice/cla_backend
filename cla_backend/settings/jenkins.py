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
        'NAME': os.environ.get('DB_USERNAME', ''),
        'TEST_NAME': 'test_cla_backend%s' % os.environ.get('BACKEND_TEST_DB_SUFFIX', ''),
        'USER': os.environ.get('DB_USERNAME', ''),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', ''),
        'PORT': os.environ.get('DB_PORT', ''),
    }
}

JENKINS_TEST_RUNNER = 'core.testing.CLADiscoverRunner'

#HOST_NAME = ""


ALLOWED_HOSTS = [
    '*'
]
