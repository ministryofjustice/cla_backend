from django.test import TestCase

from cla_eventlog.tests.base import EventTestCaseMixin


class RejectCaseEventTestCase(EventTestCaseMixin, TestCase):
    EVENT_KEY = "reject_case"

    def test_reject_case(self):
        self._test_process_with_expicit_code(["MIS", "MIS-MEANS", "MIS-OOS", "COI"])

    def test_reject_conflict(self):
        self._test_process_with_implicit_code("COI", process_kwargs={"is_conflict": True})


class AcceptCaseEventTestCase(EventTestCaseMixin, TestCase):
    EVENT_KEY = "accept_case"

    def test_accept_case(self):
        self._test_process_with_implicit_code("SPOP")


class CloseCaseEventTestCase(EventTestCaseMixin, TestCase):
    EVENT_KEY = "close_case"

    def test_close_case(self):
        self._test_process_with_implicit_code("CLSP")

    def test_close_case_with_DREFER(self):
        self._test_process_with_implicit_code("DREFER", process_kwargs={"is_debt_referral": True})
