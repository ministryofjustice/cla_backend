from django.test import TestCase

from cla_eventlog.tests.base import EventTestCaseMixin


class AssignToProviderEventTestCase(EventTestCaseMixin, TestCase):
    def test_assign_to_provider_manually(self):
        self._test_process_with_implicit_code('assign_to_provider', 'MANALC',
            process_kwargs={
                'is_manual': True
            }
        )

    def test_assign_to_provider_automatically(self):
        self._test_process_with_implicit_code('assign_to_provider', 'REFSP',
            process_kwargs={
                'is_manual': False
            }
        )


class DeferAssignmentEventTestCase(EventTestCaseMixin, TestCase):
    def test_defer_assignment(self):
        self._test_process_with_implicit_code('defer_assignment', 'CBSP')


class DeclineHelpEventTestCase(EventTestCaseMixin, TestCase):
    def test_decline_help(self):
        self._test_process_with_expicit_code(
            'decline_help', ['DESP', 'DECL', 'NRES']
        )
