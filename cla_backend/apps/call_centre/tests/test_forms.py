import datetime
from django.test import TestCase
from django.utils import timezone
from legalaid.models import CaseLog

from cla_common.constants import CASE_STATES

from core.tests.mommy_utils import make_recipe, make_user
from cla_provider.helpers import ProviderAllocationHelper

from ..forms import ProviderAllocationForm, CloseCaseForm
import mock


class ProviderAllocationFormTestCase(TestCase):
    def setUp(self):
        make_recipe('legalaid.refsp_logtype')

    @mock.patch('cla_provider.helpers.timezone.now')
    def test_save_in_office_hours(self, timezone_mock):
        timezone_mock.return_value = datetime.datetime(2014,1,1,9,1,0).replace(tzinfo=timezone.get_current_timezone())
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

        form = ProviderAllocationForm(data={'provider' : helper.get_suggested_provider(category)},
                                      providers=helper.get_qualifying_providers(category))

        self.assertTrue(form.is_valid())

        self.assertEqual(CaseLog.objects.count(),0)
        form.save(case, user)

        self.assertEqual(case.provider, provider)
        self.assertEqual(CaseLog.objects.count(),1)


    @mock.patch('cla_provider.models.timezone.now')
    @mock.patch('cla_provider.helpers.timezone.now')
    def test_save_out_office_hours(self, timezone_mock, models_timezone_mock):

        fake_day = datetime.datetime(2014,1,1,8,59,0).replace(tzinfo=timezone.get_current_timezone())
        timezone_mock.return_value = fake_day
        models_timezone_mock.return_value = fake_day

        case = make_recipe('legalaid.case')
        category = case.eligibility_check.category
        user = make_user()
        provider = make_recipe('cla_provider.provider', active=True)
        make_recipe('cla_provider.outofhoursrota',
                                        provider=provider,
                                        start_date=datetime.datetime(2013,12,30).replace(tzinfo=timezone.get_current_timezone()),
                                        end_date=datetime.datetime(2014,1,2).replace(tzinfo=timezone.get_current_timezone()),
                                        category=category
        )

        make_recipe('cla_provider.provider_allocation',
                    weighted_distribution=0.5,
                    provider=provider,
                    category=category)
        # TODO - create a ProviderAllocation for this provider with the
        #        same category as the case and a positive weighted_distribution

        helper = ProviderAllocationHelper()

        form = ProviderAllocationForm(data={'provider' : helper.get_suggested_provider(category)},
                                      providers=helper.get_qualifying_providers(category))

        self.assertTrue(form.is_valid())

        self.assertEqual(CaseLog.objects.count(),0)
        form.save(case, user)

        self.assertEqual(case.provider, provider)
        self.assertEqual(CaseLog.objects.count(),1)

    @mock.patch('cla_provider.models.timezone.now')
    @mock.patch('cla_provider.helpers.timezone.now')
    def test_save_out_office_hours_no_valid_provider(self, timezone_mock, models_timezone_mock):

        fake_day = datetime.datetime(2014,1,1,8,59,0).replace(tzinfo=timezone.get_current_timezone())
        timezone_mock.return_value = fake_day
        models_timezone_mock.return_value = fake_day

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

        suggested = helper.get_suggested_provider(category)
        self.assertIsNone(suggested)

        form = ProviderAllocationForm(data={'provider' : suggested},
                                      providers=helper.get_qualifying_providers(category))

        self.assertFalse(form.is_valid())


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
