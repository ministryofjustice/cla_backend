from django.test import TestCase
from django.conf import settings
from legalaid.models import CaseLog

from model_mommy import mommy

from cla_common.constants import CASE_STATES

from ..forms import ProviderAllocationForm, CloseCaseForm
from cla_provider.helpers import ProviderAllocationHelper

def make_recipe(model_name, **kwargs):
    return mommy.make_recipe('legalaid.tests.%s' % model_name, **kwargs)


def cla_provider_make_recipe(model_name, **kwargs):
    return mommy.make_recipe('cla_provider.tests.%s' % model_name, **kwargs)


class ProviderAllocationFormTestCase(TestCase):
    def setUp(self):
        make_recipe('assign_logtype')

    def test_save(self):
        case = make_recipe('case')
        category = case.eligibility_check.category
        user = mommy.make(settings.AUTH_USER_MODEL)
        provider = cla_provider_make_recipe('provider', active=True)
        cla_provider_make_recipe('provider_allocation',
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
        case = make_recipe('case')

        form = ProviderAllocationForm(data={},
                                      providers=[])

        self.assertFalse(form.is_valid())



class CloseCaseFormTestCase(TestCase):
    def test_save(self):
        user = mommy.make(settings.AUTH_USER_MODEL)
        case = make_recipe('case', state=CASE_STATES.OPEN)

        form = CloseCaseForm(data={})

        self.assertTrue(form.is_valid())

        form.save(case, user)

        self.assertEqual(case.state, CASE_STATES.CLOSED)
