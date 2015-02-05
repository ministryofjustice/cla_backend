from .base import *

TEST_APPS = (
    'django_pdb',
)

INSTALLED_APPS += TEST_APPS

TEST_MODE = True

ORIGINAL_DIAGNOSIS_FILE_NAME = DIAGNOSIS_FILE_NAME
DIAGNOSIS_FILE_NAME = '../tests/data/graph-2014.07.21.graphml'


REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['login'] = '10000000000/sec'

TEST_RUNNER = 'core.testing.CLADiscoverRunner'


class DisableMigrations(object):
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return "notmigrations"

MIGRATION_MODULES = DisableMigrations()
