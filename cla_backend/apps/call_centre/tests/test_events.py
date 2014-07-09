from django.test import TestCase

from cla_eventlog.tests.base import EventTestCaseMixin


class AssignToProviderEventTestCase(EventTestCaseMixin, TestCase):
    EVENT_KEY = 'assign_to_provider'

    def test_assign_to_provider_manually(self):
        self._test_process_with_implicit_code(
            'MANALC',
            process_kwargs={
                'is_manual': True
            }
        )

    def test_assign_to_provider_automatically(self):
        self._test_process_with_implicit_code(
            'REFSP',
            process_kwargs={
                'is_manual': False
            }
        )


class DeferAssignmentEventTestCase(EventTestCaseMixin, TestCase):
    EVENT_KEY = 'defer_assignment'

    def test_defer_assignment(self):
        self._test_process_with_implicit_code('CBSP')


class DeclineHelpEventTestCase(EventTestCaseMixin, TestCase):
    EVENT_KEY = 'decline_help'

    def test_decline_help(self):
        self._test_process_with_expicit_code(['DESP', 'DECL', 'NRES'])
