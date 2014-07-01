from django.test import TestCase

from cla_eventlog.tests.test_forms import BaseCaseLogFormTestCaseMixin, \
    EventSpecificLogFormTestCaseMixin

from cla_provider.forms import CloseCaseForm, AcceptCaseForm, RejectCaseForm


class AcceptCaseFormTestCase(BaseCaseLogFormTestCaseMixin, TestCase):
    FORM = AcceptCaseForm


class RejectCaseFormTestCase(EventSpecificLogFormTestCaseMixin, TestCase):
    FORM = RejectCaseForm


class CloseCaseFormTestCase(BaseCaseLogFormTestCaseMixin, TestCase):
    FORM = CloseCaseForm
