from .base import *
TEST_APPS = (
    'django_pdb',
)

INSTALLED_APPS += TEST_APPS

SOUTH_TESTS_MIGRATE = False
