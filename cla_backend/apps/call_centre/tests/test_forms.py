import mock
import datetime
from django.test import TestCase
from django.utils import timezone

from core.tests.mommy_utils import make_recipe, make_user
from cla_eventlog.tests.test_forms import BaseCaseLogFormTestCaseMixin, \
    EventSpecificLogFormTestCaseMixin

from cla_eventlog.models import Log

from cla_provider.helpers import ProviderAllocationHelper
from call_centre.forms import DeferAssignmentCaseForm, ProviderAllocationForm, \
    DeclineAllSpecialistsCaseForm


def _mock_datetime_now_with(date, *mocks):
    for mock in mocks:
        mock.return_value = date.replace(
            tzinfo=timezone.get_current_timezone())

class ProviderAllocationFormTestCase(TestCase):

    @mock.patch('cla_provider.helpers.timezone.now')
    def test_save_in_office_hours(self, timezone_mock):
        _mock_datetime_now_with(datetime.datetime(2014, 1, 1, 9, 1, 0),
                                timezone_mock)
        case = make_recipe('legalaid.case')
        category = case.eligibility_check.category
        case.matter_type1 = make_recipe('legalaid.matter_type1',
                                        category=category)
        case.matter_type2 = make_recipe('legalaid.matter_type2',
                                        category=category)
        case.save()
        user = make_user()
        provider = make_recipe('cla_provider.provider', active=True)
        make_recipe('cla_provider.provider_allocation',
                    weighted_distribution=0.5,
                    provider=provider,
                    category=category)

        helper = ProviderAllocationHelper()
        form = ProviderAllocationForm(case=case, data={
            'provider': helper.get_suggested_provider(category).pk},
            providers=helper.get_qualifying_providers(
            category))

        self.assertTrue(form.is_valid())

        self.assertEqual(Log.objects.count(), 0)
        form.save(user)

        self.assertEqual(case.provider, provider)
        self.assertEqual(Log.objects.count(), 1)

    @mock.patch('cla_provider.models.timezone.now')
    @mock.patch('cla_provider.helpers.timezone.now')
    def test_save_out_office_hours(self, timezone_mock, models_timezone_mock):
        _mock_datetime_now_with(datetime.datetime(2014, 1, 1, 8, 59, 0),
                                timezone_mock, models_timezone_mock)

        case = make_recipe('legalaid.case')
        category = case.eligibility_check.category

        case.matter_type1 = make_recipe('legalaid.matter_type1',
                                        category=category)
        case.matter_type2 = make_recipe('legalaid.matter_type2',
                                        category=category)
        case.save()

        user = make_user()
        provider = make_recipe('cla_provider.provider', active=True)
        make_recipe('cla_provider.outofhoursrota',
                    provider=provider,
                    start_date=datetime.datetime(2013, 12, 30).replace(
                        tzinfo=timezone.get_current_timezone()),
                    end_date=datetime.datetime(2014, 1, 2).replace(
                        tzinfo=timezone.get_current_timezone()),
                    category=category
                    )

        make_recipe('cla_provider.provider_allocation',
                    weighted_distribution=0.5,
                    provider=provider,
                    category=category)
        # TODO - create a ProviderAllocation for this provider with the
        # same category as the case and a positive weighted_distribution

        helper = ProviderAllocationHelper()

        form = ProviderAllocationForm(case=case, data={
            'provider': helper.get_suggested_provider(category).pk},
            providers=helper.get_qualifying_providers(
            category))

        self.assertTrue(form.is_valid())

        self.assertEqual(Log.objects.count(), 0)
        form.save(user)

        self.assertEqual(case.provider, provider)
        self.assertEqual(Log.objects.count(), 1)

    @mock.patch('cla_provider.models.timezone.now')
    @mock.patch('cla_provider.helpers.timezone.now')
    def test_save_out_office_hours_no_valid_provider(self, timezone_mock,
                                                     models_timezone_mock):
        _mock_datetime_now_with(datetime.datetime(2014, 1, 1, 8, 59, 0),
                                timezone_mock, models_timezone_mock)

        case = make_recipe('legalaid.case')
        category = case.eligibility_check.category

        case.matter_type1 = make_recipe('legalaid.matter_type1',
                                        category=category)
        case.matter_type2 = make_recipe('legalaid.matter_type2',
                                        category=category)
        case.save()

        provider = make_recipe('cla_provider.provider', active=True)

        make_recipe('cla_provider.provider_allocation',
                    weighted_distribution=0.5,
                    provider=provider,
                    category=category)
        # TODO - create a ProviderAllocation for this provider with the
        # same category as the case and a positive weighted_distribution

        helper = ProviderAllocationHelper()

        suggested = helper.get_suggested_provider(category)
        self.assertIsNone(suggested)

        form = ProviderAllocationForm(case=case, data={
            'provider': suggested.pk if suggested else None},
            providers=helper.get_qualifying_providers(
            category))

        self.assertFalse(form.is_valid())

    def test_not_valid_with_no_valid_provider_for_category(self):
        case = make_recipe('legalaid.case')

        form = ProviderAllocationForm(case=case, data={},
                                      providers=[])

        self.assertFalse(form.is_valid())

    @mock.patch('cla_provider.models.timezone.now')
    @mock.patch('cla_provider.helpers.timezone.now')
    def test_save_without_matter_type_both(self, timezone_mock,
                                           models_timezone_mock):
        _mock_datetime_now_with(datetime.datetime(2014, 1, 1, 12, 59, 0),
                                timezone_mock, models_timezone_mock)

        case = make_recipe('legalaid.case')
        category = case.eligibility_check.category

        provider = make_recipe('cla_provider.provider', active=True)

        make_recipe('cla_provider.provider_allocation',
                    weighted_distribution=0.5,
                    provider=provider,
                    category=category)

        helper = ProviderAllocationHelper()
        form = ProviderAllocationForm(case=case, data={
            'provider': helper.get_suggested_provider(category).pk},
            providers=helper.get_qualifying_providers(
            category))

        self.assertFalse(form.is_valid())
        self.assertDictEqual(form.errors, {'__all__': [
            u"Can't assign to specialist provider without setting matter_type1 and matter_type2"]})

    @mock.patch('cla_provider.models.timezone.now')
    @mock.patch('cla_provider.helpers.timezone.now')
    def test_save_without_matter_type_only_mt1(self, timezone_mock,
                                               models_timezone_mock):
        _mock_datetime_now_with(datetime.datetime(2014, 1, 1, 12, 59, 0),
                                timezone_mock, models_timezone_mock)

        case = make_recipe('legalaid.case')
        category = case.eligibility_check.category

        provider = make_recipe('cla_provider.provider', active=True)

        make_recipe('cla_provider.provider_allocation',
                    weighted_distribution=0.5,
                    provider=provider,
                    category=category)
        case.matter_type1 = make_recipe('legalaid.matter_type1',
                                        category=category)
        case.save()

        helper = ProviderAllocationHelper()
        form = ProviderAllocationForm(case=case, data={
            'provider': helper.get_suggested_provider(category).pk},
            providers=helper.get_qualifying_providers(
            category))

        self.assertFalse(form.is_valid())
        self.assertDictEqual(form.errors, {'__all__': [
            u"Can't assign to specialist provider without setting matter_type1 and matter_type2"]})

    @mock.patch('cla_provider.models.timezone.now')
    @mock.patch('cla_provider.helpers.timezone.now')
    def test_save_without_matter_type_category_mismatch(self, timezone_mock,
                                               models_timezone_mock):
        _mock_datetime_now_with(datetime.datetime(2014, 1, 1, 12, 59, 0),
                                timezone_mock, models_timezone_mock)

        case = make_recipe('legalaid.case')
        category = case.eligibility_check.category

        provider = make_recipe('cla_provider.provider', active=True)
        make_recipe('cla_provider.outofhoursrota',
                    provider=provider,
                    start_date=datetime.datetime(2013, 12, 30).replace(
                        tzinfo=timezone.get_current_timezone()),
                    end_date=datetime.datetime(2014, 1, 2).replace(
                        tzinfo=timezone.get_current_timezone()),
                    category=category
                    )

        make_recipe('cla_provider.provider_allocation',
                    weighted_distribution=0.5,
                    provider=provider,
                    category=category)
        case.matter_type1 = make_recipe('legalaid.matter_type1',
                                        category=category)
        other_category = make_recipe('legalaid.category')
        case.matter_type2 = make_recipe('legalaid.matter_type2', category=other_category)
        case.save()

        helper = ProviderAllocationHelper()
        form = ProviderAllocationForm(case=case, data={
            'provider': helper.get_suggested_provider(category).pk},
            providers=helper.get_qualifying_providers(
            category))

        self.assertFalse(form.is_valid())
        self.assertDictEqual(form.errors, {'__all__': [
            u'Category of matter type 1: {} must match category of matter type 2: {}'.format(category.name, other_category.name),
            u'Category of Matter Types: {c1},{c2} must match category of case: {c1}'.format(c1=category.name, c2=other_category.name)]})


class DeferAssignmentCaseFormTestCase(BaseCaseLogFormTestCaseMixin, TestCase):
    FORM = DeferAssignmentCaseForm


class DeclineAllSpecialistsCaseFormTestCase(EventSpecificLogFormTestCaseMixin,
                                            TestCase):
    FORM = DeclineAllSpecialistsCaseForm
