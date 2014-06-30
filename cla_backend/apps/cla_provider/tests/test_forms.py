from django.test import TestCase

from legalaid.tests.base import BaseCaseLogFormTestCase, EventSpecificLogFormTestCase

from cla_provider.forms import CloseCaseForm, AcceptCaseForm, RejectCaseForm


class AcceptCaseFormTestCase(BaseCaseLogFormTestCase, TestCase):
    FORM = AcceptCaseForm


class RejectCaseFormTestCase(EventSpecificLogFormTestCase, TestCase):
    FORM = RejectCaseForm


class CloseCaseFormTestCase(BaseCaseLogFormTestCase, TestCase):
    FORM = CloseCaseForm
