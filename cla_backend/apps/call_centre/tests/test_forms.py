from django.test import TestCase
from legalaid.models import CaseLog

from cla_common.constants import CASE_STATES

from core.tests.mommy_utils import make_recipe, make_user
from cla_provider.helpers import ProviderAllocationHelper

from ..forms import ProviderAllocationForm, CloseCaseForm


class ProviderAllocationFormTestCase(TestCase):
    def setUp(self):
        make_recipe('legalaid.assign_logtype')

    def test_save(self):
        case = make_recipe('legalaid.case')
        category = case.eligibility_check.category
        user = make_user()
        provider = make_recipe('cla_provider.provider', active=True)
        make_recipe('cla_provider.provider_allocation',
                                      weighted_distribution=0.5,
                                      provider=provider,
                                      category=category)
        # TODO - create a ProviderAllocation for this provider with the
        #        same category as the case and a positive weighted_distribution

        helper = ProviderAllocationHelper()

        form = ProviderAllocationForm(data={'provider' : helper.get_random_provider(category)},
                                      providers=helper.get_qualifying_providers(category))

        self.assertTrue(form.is_valid())

        self.assertEqual(CaseLog.objects.count(),0)
        form.save(case, user)

        self.assertEqual(case.provider, provider)
        self.assertEqual(CaseLog.objects.count(),1)

    def test_not_valid_with_no_valid_provider_for_category(self):
        case = make_recipe('legalaid.case')

        form = ProviderAllocationForm(data={},
                                      providers=[])

        self.assertFalse(form.is_valid())



class CloseCaseFormTestCase(TestCase):
    def test_save(self):
        user = make_user()
        case = make_recipe('legalaid.case', state=CASE_STATES.OPEN)

        form = CloseCaseForm(data={})

        self.assertTrue(form.is_valid())

        form.save(case, user)

        self.assertEqual(case.state, CASE_STATES.CLOSED)
