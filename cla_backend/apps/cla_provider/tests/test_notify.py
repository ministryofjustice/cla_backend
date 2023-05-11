from django.test import TestCase
from core.tests.mommy_utils import make_recipe

from cla_provider.helpers import notify_case_assigned


class Notify(TestCase):
    def test_notify_case_assigned_success(self):
        provider = make_recipe("cla_provider.provider", email_address="mishkat.najam@digital.justice.gov.uk", active=True)
        case = make_recipe("legalaid.case", outcome_code="SPOR")

        notify_case_assigned(provider, case)
