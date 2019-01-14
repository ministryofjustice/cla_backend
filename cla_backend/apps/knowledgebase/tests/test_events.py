from django.test import TestCase

from cla_eventlog.tests.base import EventTestCaseMixin


class AlternativeHelpEventTestCase(EventTestCaseMixin, TestCase):
    EVENT_KEY = "alternative_help"

    def test_assign_alternative_help(self):
        self._test_process_with_expicit_code(["COSPF", "IRKB", "SPFN", "SPFM"])
