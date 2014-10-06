import mock
import datetime
from django.test import TestCase
from django.utils import timezone

from core.tests.mommy_utils import make_recipe, make_user
from cla_eventlog.tests.test_forms import BaseCaseLogFormTestCaseMixin, \
    EventSpecificLogFormTestCaseMixin

from cla_eventlog.models import Log

from legalaid.models import Case

from cla_provider.helpers import ProviderAllocationHelper
from call_centre.forms import DeferAssignmentCaseForm, ProviderAllocationForm, \
    DeclineHelpCaseForm, CallMeBackForm


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


class DeclineHelpCaseFormTestCase(EventSpecificLogFormTestCaseMixin,
                                            TestCase):
    FORM = DeclineHelpCaseForm


class CallMeBackFormTestCase(BaseCaseLogFormTestCaseMixin,
                                            TestCase):
    FORM = CallMeBackForm

    def _strftime(self, date):
        return date.strftime('%Y-%m-%d %H:%M')

    def _get_next_mon(self):
        now = timezone.now()
        mon = now + datetime.timedelta(days=7-now.weekday())
        return mon.replace(hour=10, minute=0, second=0, microsecond=0)

    def get_default_data(self, **kwargs):
        dt = kwargs.get(
            'datetime', self._strftime(self._get_next_mon())
        )
        return {
            'notes': 'lorem ipsum',
            'datetime': dt
        }

    def test_save_successfull(self):
        case = make_recipe('legalaid.case')
        self.assertEqual(Log.objects.count(), 0)

        dt = self._get_next_mon()
        data = self.get_default_data(datetime=self._strftime(dt))
        form = self.FORM(case=case, data=data)

        self.assertTrue(form.is_valid())

        form.save(self.user)

        case = Case.objects.get(pk=case.pk)

        self.assertEqual(Log.objects.count(), 1)
        log = Log.objects.all()[0]

        self.assertEqual(
            log.notes,
            'Callback scheduled for %s. lorem ipsum' % timezone.localtime(dt).strftime("%d/%m/%Y %H:%M")
        )
        self.assertEqual(log.created_by, self.user)
        self.assertEqual(log.case, case)

        self.assertEqual(
            case.requires_action_at,
            datetime.datetime(
                year=dt.year, month=dt.month, day=dt.day,
                hour=dt.hour, minute=dt.minute, tzinfo=timezone.utc
            )
        )

    def test_invalid_datetime(self):
        case = make_recipe('legalaid.case')
        self.assertEqual(Log.objects.count(), 0)

        def _test(case, datetime, error_msg):
            data = self.get_default_data()
            data['datetime'] = datetime
            form = self.FORM(case=case, data=data)

            self.assertFalse(form.is_valid())

            self.assertEqual(len(form.errors), 1)
            self.assertItemsEqual(
                form.errors['datetime'], [error_msg]
            )

            # nothing has changed
            case = Case.objects.get(pk=case.pk)
            self.assertEqual(Log.objects.count(), 0)

        # required datetime
        _test(case, None, u'This field is required.')

        # invalid format
        _test(
            case,
            timezone.now().strftime('%Y/%m/%d %H:%M'),
            u'Enter a valid date/time.'
        )

        # datetime in the past
        _test(
            case,
            self._strftime(timezone.now()),
            u'Specify a date not in the current half hour.'
        )

        _test(
            case,
            self._strftime(timezone.now() + datetime.timedelta(minutes=30)),
            u'Specify a date not in the current half hour.'
        )

        # Sat at 12.31
        sat = timezone.now() + datetime.timedelta(days=12-timezone.now().weekday())
        sat = sat.replace(hour=11, minute=31, second=0, microsecond=0)

        _test(
            case,
            self._strftime(sat),
            u'Specify a date within working hours.'
        )

        # Sun at 10am
        sun = timezone.now() + datetime.timedelta(days=13-timezone.now().weekday())
        sun = sun.replace(hour=9, minute=0, second=0, microsecond=0)

        _test(
            case,
            self._strftime(sun),
            u'Specify a date within working hours.'
        )

        # Mon at 8.59
        mon = timezone.now() + datetime.timedelta(days=7-timezone.now().weekday())
        mon = mon.replace(hour=7, minute=59, second=0, microsecond=0)

        _test(
            case,
            self._strftime(mon),
            u'Specify a date within working hours.'
        )

        # Mon at 20.01
        mon = timezone.now() + datetime.timedelta(days=7-timezone.now().weekday())
        mon = mon.replace(hour=19, minute=1, second=0, microsecond=0)

        _test(
            case,
            self._strftime(mon),
            u'Specify a date within working hours.'
        )
