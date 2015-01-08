from django.core.management import call_command
from django.test.utils import get_runner
from django.conf import settings


# use jenkins runner if present otherwise the default django one
if 'django_jenkins' in settings.INSTALLED_APPS:
    base_runner = 'django_jenkins.runner.CITestSuiteRunner'
else:
    base_runner = 'django.test.runner.DiscoverRunner'


class CLADiscoverRunner(get_runner(settings, base_runner)):
    """
    Overrides the default Runner and loads the initial_groups fixture.
    This is because migrations are switched off during testing but
    we do need `initial_groups` in order for the tests to pass.
    """
    def setup_databases(self, **kwargs):
        ret = super(CLADiscoverRunner, self).setup_databases(**kwargs)
        call_command('loaddata', 'initial_groups')
        return ret
