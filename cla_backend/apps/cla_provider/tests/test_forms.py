from django.test import TestCase

from cla_common.constants import CASE_STATES

from legalaid.tests.base import BaseStateFormTestCase

from ..forms import CloseCaseForm, AcceptCaseForm, RejectCaseForm


class AcceptCaseFormTestCase(BaseStateFormTestCase, TestCase):
    FORM = AcceptCaseForm
    VALID_OUTCOME_CODE = 'CODE_ACCEPTED'
    EXPECTED_CASE_STATE = CASE_STATES.ACCEPTED


class RejectCaseFormTestCase(BaseStateFormTestCase, TestCase):
    FORM = RejectCaseForm
    VALID_OUTCOME_CODE = 'CODE_REJECTED'
    EXPECTED_CASE_STATE = CASE_STATES.REJECTED


class CloseCaseFormTestCase(BaseStateFormTestCase, TestCase):
    FORM = CloseCaseForm
    VALID_OUTCOME_CODE = 'CODE_CLOSED'
    EXPECTED_CASE_STATE = CASE_STATES.CLOSED
