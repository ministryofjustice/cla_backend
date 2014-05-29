from django.test import TestCase
from legalaid.models import CaseLog

from cla_common.constants import CASE_STATES

from core.tests.mommy_utils import make_recipe, make_user
from legalaid.tests.base import BaseStateFormTestCase
from legalaid.models import Case

from cla_provider.helpers import ProviderAllocationHelper
from ..forms import ProviderAllocationForm, CloseCaseForm, \
    DeclineAllSpecialistsCaseForm


class ProviderAllocationFormTestCase(TestCase):
    def setUp(self):
        make_recipe('legalaid.refsp_logtype')

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

        form = ProviderAllocationForm(
            case=case,
            data={'provider': helper.get_random_provider(category)},
            providers=helper.get_qualifying_providers(category)
        )

        self.assertTrue(form.is_valid())

        self.assertEqual(CaseLog.objects.count(),0)
        form.save(user)

        self.assertEqual(case.provider, provider)
        self.assertEqual(CaseLog.objects.count(),1)

    def test_not_valid_with_no_valid_provider_for_category(self):
        case = make_recipe('legalaid.case')

        form = ProviderAllocationForm(case=case, data={},
                                      providers=[])

        self.assertFalse(form.is_valid())


class CloseCaseFormTestCase(TestCase):
    def test_save(self):
        user = make_user()
        case = make_recipe('legalaid.case', state=CASE_STATES.OPEN)

        form = CloseCaseForm(case=case, data={})

        self.assertTrue(form.is_valid())

        form.save(user)

        self.assertEqual(case.state, CASE_STATES.CLOSED)


class DeclineAllSpecialistsCaseFormTestCase(BaseStateFormTestCase, TestCase):
    FORM = DeclineAllSpecialistsCaseForm
    VALID_OUTCOME_CODE = 'CODE_DECLINED_ALL_SPECIALISTS'
    EXPECTED_CASE_STATE = CASE_STATES.CLOSED

    def test_invalid_if_case_already_assigned(self):
        provider = make_recipe('cla_provider.provider')
        case = make_recipe('legalaid.case', state=CASE_STATES.OPEN, provider=provider)

        form = self.FORM(case=case, data={
            'outcome_code': self.VALID_OUTCOME_CODE,
            'outcome_notes': 'lorem ipsum'
        })

        self.assertFalse(form.is_valid())

        self.assertItemsEqual(
            form.errors, {'__all__': [u'Case currently assigned to a provider']}
        )
