from collections import defaultdict
import random
import mock
import datetime

from django.utils import timezone
from django.test import TestCase

from core.tests.mommy_utils import make_recipe
from cla_provider.models import ProviderPreAllocation
from cla_provider.helpers import ProviderDistributionHelper, \
    ProviderAllocationHelper
from legalaid.forms import get_sla_time

class SLATimeHelperTestCase(TestCase):

    def _get_next_mon(self):
        now = timezone.now()
        mon = now + datetime.timedelta(days=7-now.weekday())
        return mon.replace(hour=10, minute=0, second=0, microsecond=0)

    def test_get_sla_time_simple_delta_works(self):
        with mock.patch('cla_common.call_centre_availability.bank_holidays', return_value=[]) as bank_hol:
            d = self._get_next_mon()
            self.assertEqual(get_sla_time(d, 15), d + datetime.timedelta(minutes=15))
            self.assertTrue(bank_hol.called)

    def test_get_sla_time_delta_past_end_of_weekday_works(self):
        with mock.patch('cla_common.call_centre_availability.bank_holidays', return_value=[]) as bank_hol:
            d = self._get_next_mon().replace(hour=19, minute=59, tzinfo=timezone.get_default_timezone())
            next_day = (d + datetime.timedelta(days=1)).replace(hour=9, minute=14, tzinfo=timezone.get_default_timezone())
            self.assertEqual(get_sla_time(d, 15), next_day)

            next_day_120 = next_day.replace(hour=10, minute=59)
            self.assertEqual(get_sla_time(d, 120), next_day_120)

            next_day_480 = next_day.replace(hour=16, minute=59)
            self.assertEqual(get_sla_time(d, 480), next_day_480)

            self.assertTrue(bank_hol.called)

    def test_get_sla_time_delta_past_end_of_saturday_works(self):
        with mock.patch('cla_common.call_centre_availability.bank_holidays', return_value=[]) as bank_hol:
            d = self._get_next_mon().replace(hour=12, minute=29, tzinfo=timezone.get_default_timezone())
            next_sat = (d + datetime.timedelta(days=5))
            next_mon = (next_sat + datetime.timedelta(days=2)).replace(hour=9, minute=14, tzinfo=timezone.get_default_timezone())
            self.assertEqual(get_sla_time(next_sat, 15), next_mon)
            self.assertTrue(bank_hol.called)

    def test_get_sla_time_delta_past_end_of_weekday_with_next_day_a_bank_hol_works(self):
        d = self._get_next_mon().replace(hour=19, minute=44, tzinfo=timezone.get_default_timezone())
        next_day = d + datetime.timedelta(days=1)
        next_day_as_bank_hol = datetime.datetime.combine(next_day, datetime.time())
        next_day_plus1 = (next_day + datetime.timedelta(days=1)).replace(hour=10, minute=44, tzinfo=timezone.get_default_timezone())
        next_day_plus1_480 = (next_day + datetime.timedelta(days=1)).replace(hour=16, minute=44, tzinfo=timezone.get_default_timezone())
        with mock.patch('cla_common.call_centre_availability.bank_holidays', return_value=[next_day_as_bank_hol]) as bank_hol:
            end_of_day = d.replace(hour=19, minute=59, tzinfo=timezone.get_default_timezone())
            self.assertEqual(get_sla_time(d, 15), end_of_day)
            self.assertEqual(get_sla_time(d, 120), next_day_plus1)
            self.assertEqual(get_sla_time(d, 480), next_day_plus1_480)
            self.assertTrue(bank_hol.called)


    def test_lots_of_dates_dont_break_it(self):
        with mock.patch('cla_common.call_centre_availability.bank_holidays', return_value=[]) as bank_hol:
            start_date = timezone.now().replace(hour=9, minute=0)

            dates = [start_date + datetime.timedelta(days=x) for x in range(1, 100)]
            for date in dates:
                random_hour = random.randint(9, 12)
                random_minute = random.randint(0, 29)
                date = date.replace(hour=random_hour, minute=random_minute, second=0, microsecond=0, tzinfo=timezone.get_default_timezone())
                get_sla_time(date, 15)
                get_sla_time(date, 120)
                get_sla_time(date, 480)
                self.assertTrue(bank_hol.called)

class ProviderAllocationHelperTestCase(TestCase):

    def setUp(self):
        self.category = make_recipe('legalaid.category')
        self.helper = ProviderAllocationHelper()
        self.date = timezone.now().replace(hour=0, minute=0, second=0)
        self.provider_allocations = make_recipe('cla_provider.provider_allocation',
                                                category=self.category,
                                                weighted_distribution=1.0,
                                                provider__active=True,
                                                _quantity=10)

    @mock.patch('cla_provider.helpers.ProviderAllocationHelper._get_random_provider')
    @mock.patch('cla_provider.helpers.ProviderDistributionHelper.get_distribution')
    def test_best_fit_provider_shortcut_no_cases_for_today(self, mocked_helper, mocked_random_provider_helper):
        mocked_helper.return_value = {}
        mocked_random_provider_helper.return_value = 'TEST'

        ret = self.helper._get_best_fit_provider(self.category)
        self.assertTrue(mocked_helper.called)
        self.assertTrue(mocked_random_provider_helper.called)
        self.assertEqual(ret, 'TEST')


    @mock.patch('cla_provider.helpers.ProviderAllocationHelper._get_random_provider')
    @mock.patch('cla_provider.helpers.ProviderDistributionHelper.get_distribution')
    def test_best_fit_provider_shortcut_current_is_ideal(self, mocked_helper, mocked_random_provider_helper):

        pd_helper = ProviderDistributionHelper(self.date)

        mocked_helper.return_value = pd_helper.make_ideal(10, self.provider_allocations)
        mocked_random_provider_helper.return_value = 'TEST'

        ret = self.helper._get_best_fit_provider(self.category)
        self.assertTrue(mocked_helper.called)
        self.assertTrue(mocked_random_provider_helper.called)
        self.assertEqual(ret, 'TEST')

    @mock.patch('cla_provider.helpers.ProviderAllocationHelper._get_random_provider')
    @mock.patch('cla_provider.helpers.ProviderDistributionHelper.get_distribution')
    def test_best_fit_provider_current_is_notideal_only1(self, mocked_helper, mocked_random_provider_helper):

        pd_helper = ProviderDistributionHelper(self.date)

        ideal = pd_helper.make_ideal(10, self.provider_allocations)
        ideal[ideal.keys()[0]] = 0.0

        mocked_helper.return_value = ideal
        mocked_random_provider_helper.return_value = 'TEST'

        ret = self.helper._get_best_fit_provider(self.category)
        self.assertTrue(mocked_helper.called)
        self.assertFalse(mocked_random_provider_helper.called)
        self.assertNotEqual(ret, 'TEST')
        self.assertEqual(ret.id, ideal.keys()[0])

    @mock.patch('cla_provider.helpers.ProviderAllocationHelper._get_random_provider')
    @mock.patch('cla_provider.helpers.ProviderDistributionHelper.get_distribution')
    def test_best_fit_provider_current_is_notideal_2(self, mocked_helper, mocked_random_provider_helper):

        pd_helper = ProviderDistributionHelper(self.date)

        ideal = pd_helper.make_ideal(10, self.provider_allocations)
        ideal[ideal.keys()[0]] = 0.0
        ideal[ideal.keys()[1]] = 0.0

        mocked_helper.return_value = ideal
        mocked_random_provider_helper.return_value = 'TEST'

        ret = self.helper._get_best_fit_provider(self.category)
        self.assertTrue(mocked_helper.called)
        mocked_random_provider_helper.assert_called_once_with(self.category, limit_choices_to=ideal.keys()[:2])
        self.assertEqual(ret, 'TEST')

class ProviderDistributionHelperTestCase(TestCase):

    def setUp(self):
        self.category = make_recipe('legalaid.category')
        self.category2 = make_recipe('legalaid.category')
        self.provider_allocations = make_recipe('cla_provider.provider_allocation', category=self.category, weighted_distribution=1.0, _quantity=10)

        self.uneven_provider_allocations = make_recipe('cla_provider.provider_allocation', category=self.category, weighted_distribution=1.0, _quantity=5)
        self.uneven_provider_allocations.extend(make_recipe('cla_provider.provider_allocation', category=self.category, weighted_distribution=2.0, _quantity=5))

        self.date = timezone.now().replace(hour=0, minute=0, second=0)
        self.helper = ProviderDistributionHelper(self.date)


    def _check_dist(self, num, allocs):
        ideal_dist = self.helper.make_ideal(num, allocs)
        self.assertAlmostEqual(num, sum(ideal_dist.values()), places=2)
        self.assertEqual(len(ideal_dist), len(allocs))

        pa_grouped_by_weight = defaultdict(list)
        for pa in allocs:
            pa_grouped_by_weight[pa.weighted_distribution].append(pa.provider_id)
        for group, vals in pa_grouped_by_weight.items():
            self.assertEqual(len(set([v for k, v in ideal_dist.items() if k in vals])), 1) # if you have the same weight then you should have the same ideal number

        return ideal_dist

    def _assign_new_case_to_provider(self, provider):
        c1 = make_recipe('legalaid.eligible_case')
        c1.diagnosis.category = self.category
        c1.assign_to_provider(provider)
        c1.diagnosis.save()
        c1.save()
        return c1

    def _pre_allocate_case_to_provider(self, provider):
        c1 = make_recipe('legalaid.eligible_case')
        c1.diagnosis.category = self.category
        c1.diagnosis.save()
        c1.save()
        ProviderPreAllocation.objects.pre_allocate(self.category, provider, c1)
        return c1

    def test_make_idea_makes_valid_ideal_distribution_all_equal(self):
        for n in range(0, 10):
            self._check_dist(n, self.provider_allocations)

        self._check_dist(10, self.provider_allocations[:1])

    def test_make_idea_makes_valid_ideal_distribution_some_unequal(self):
        for n in range(0, 10):
            self._check_dist(n, self.uneven_provider_allocations)


    def test_get_distribution_works_ignore_preallocs(self):
        actual_dist = self.helper.get_distribution(self.category, include_pre_allocations=False)
        self.assertEqual(actual_dist, {})

        provider_1 = self.provider_allocations[0].provider
        self._assign_new_case_to_provider(provider_1)
        self._pre_allocate_case_to_provider(provider_1)

        actual_dist_after = self.helper.get_distribution(self.category, include_pre_allocations=False)
        self.assertNotEqual(actual_dist_after, actual_dist)

        self.assertEqual(actual_dist_after, {provider_1.id: 1})

    def test_get_distribution_works_with_preallocs(self):
        actual_dist = self.helper.get_distribution(self.category, include_pre_allocations=True)
        self.assertEqual(actual_dist, {})

        provider_1 = self.provider_allocations[0].provider
        self._assign_new_case_to_provider(provider_1)
        self._pre_allocate_case_to_provider(provider_1)

        actual_dist_after = self.helper.get_distribution(self.category, include_pre_allocations=True)
        self.assertNotEqual(actual_dist_after, actual_dist)

        self.assertEqual(actual_dist_after, {provider_1.id: 2})


