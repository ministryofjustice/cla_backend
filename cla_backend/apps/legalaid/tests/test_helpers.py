from collections import defaultdict
import random
import mock
import datetime

from django.utils import timezone
from django.test import TestCase

from unittest import skip
from core.tests.mommy_utils import make_recipe
from cla_provider.models import ProviderPreAllocation
from cla_provider.helpers import ProviderDistributionHelper, ProviderAllocationHelper
from legalaid.forms import get_sla_time


class SLATimeHelperTestCase(TestCase):

    monday = 1
    saturday = 6
    tz = timezone.get_default_timezone()

    # 'get_sla_time()' uses the 'cla_common.call_centre_availability.available_days()' function,
    # which in turn uses 'current_datetime()' and 'datetime.datetime.now()'.
    #
    # 'get_sla_time()' calculates elapsed time within operator business hours, which requires to roll over
    # and the end of day (19:59 + 2 minutes is next day 9:01).
    #
    # The roll over uses 'available_days()' and the day the test is running which means we **cannot** test
    # with fixed dates, only dates guaranteed to be after today.
    def _datetime(self, iso_day_of_week=1, hour=10, minute=15):
        today = datetime.date.today()
        next_day_offset = 7 - today.isoweekday() + iso_day_of_week
        next_week_day = today + datetime.timedelta(days=next_day_offset)
        return timezone.make_aware(datetime.datetime.combine(next_week_day, datetime.time(hour, minute)), self.tz)

    # This method exists to safely calculate the resulting date's timezone.
    # It was necessary when we calculated a "future date" that had a different timezone than the "original date".
    #
    # Example: https://circleci.com/gh/ministryofjustice/cla_backend/126
    #   self.assertEqual(get_sla_time(next_sat, 15), next_mon)
    #   AssertionError: datetime.datetime(2018, 10, 29, 10, 14, tzinfo=<DstTzInfo 'Europe/London' GMT0:00:00 STD>) != datetime.datetime(2018, 10, 29, 9, 14, tzinfo=<UTC>)
    #
    # (where 'next_sat' was 27/10/2018, still in British Summer Time)
    #
    # Ideally, we would make 'available_days()' take an argument as the "base" date for business days instead.
    def _change(self, time, plus_days=0, hour=10, minute=0):
        naive_time = timezone.make_naive(time, self.tz)
        offset = naive_time + datetime.timedelta(days=plus_days)
        return timezone.make_aware(offset, self.tz).replace(hour=hour, minute=minute)

    def test_get_sla_time_15_minutes_delta_during_working_day_keeps_the_same_day(self):
        with mock.patch("cla_common.call_centre_availability.bank_holidays", return_value=[]) as bank_hol:
            base = self._datetime(iso_day_of_week=self.monday, hour=10, minute=15)
            target = self._datetime(iso_day_of_week=self.monday, hour=10, minute=30)
            self.assertEqual(get_sla_time(base, 15), target)
            self.assertTrue(bank_hol.called)

    def test_get_sla_time_adding_time_past_end_of_weekday_rolls_over_to_next_working_day(self):
        with mock.patch("cla_common.call_centre_availability.bank_holidays", return_value=[]) as bank_hol:
            end_of_weekday = self._datetime(iso_day_of_week=self.monday, hour=19, minute=59)

            next_day_15_mins = self._change(end_of_weekday, plus_days=1, hour=9, minute=14)
            next_day_2_hours = self._change(end_of_weekday, plus_days=1, hour=10, minute=59)
            next_day_8_hours = self._change(end_of_weekday, plus_days=1, hour=16, minute=59)

            self.assertEqual(get_sla_time(end_of_weekday, 15), next_day_15_mins)
            self.assertEqual(get_sla_time(end_of_weekday, 120), next_day_2_hours)
            self.assertEqual(get_sla_time(end_of_weekday, 480), next_day_8_hours)

            self.assertTrue(bank_hol.called)

    def test_get_sla_time_adding_time_on_saturday_end_of_day_rolls_over_to_next_working_day(self):
        with mock.patch("cla_common.call_centre_availability.bank_holidays", return_value=[]) as bank_hol:
            saturday_end_of_day = self._datetime(iso_day_of_week=self.saturday, hour=12, minute=29)
            next_monday = self._change(saturday_end_of_day, plus_days=2, hour=9, minute=14)
            self.assertEqual(get_sla_time(saturday_end_of_day, 15), next_monday)
            self.assertTrue(bank_hol.called)

    def test_get_sla_time_adding_time_before_bank_holiday_rolls_over_to_working_day_after_holiday(self):
        almost_end_of_day = self._datetime(iso_day_of_week=self.monday, hour=19, minute=44)
        fake_bank_holiday = timezone.make_naive(
            self._change(almost_end_of_day, plus_days=1, hour=0, minute=0), self.tz
        )

        with mock.patch(
            "cla_common.call_centre_availability.bank_holidays", return_value=[fake_bank_holiday]
        ) as bank_hol:
            end_of_day = self._change(almost_end_of_day, plus_days=0, hour=19, minute=59)
            day_after_bank_holiday = self._change(almost_end_of_day, plus_days=2, hour=10, minute=44)
            self.assertEqual(get_sla_time(almost_end_of_day, 15), end_of_day)
            self.assertEqual(get_sla_time(almost_end_of_day, 120), day_after_bank_holiday)
            self.assertTrue(bank_hol.called)

    def test_lots_of_dates_dont_break_it(self):
        with mock.patch("cla_common.call_centre_availability.bank_holidays", return_value=[]) as bank_hol:
            start_date = timezone.now().replace(hour=9, minute=0)

            dates = [start_date + datetime.timedelta(days=x) for x in range(1, 300)]
            for date in dates:
                random_hour = random.randint(0, 23)
                random_minute = random.randint(0, 59)
                date = date.replace(hour=random_hour, minute=random_minute, second=0, microsecond=0)
                get_sla_time(date, 15)
                get_sla_time(date, 120)
                get_sla_time(date, 480)
                self.assertTrue(bank_hol.called)


class ProviderAllocationHelperTestCase(TestCase):
    def setUp(self):
        self.category = make_recipe("legalaid.category")
        self.helper = ProviderAllocationHelper()
        self.date = timezone.now().replace(hour=0, minute=0, second=0)
        self.provider_allocations = make_recipe(
            "cla_provider.provider_allocation",
            category=self.category,
            weighted_distribution=1.0,
            provider__active=True,
            _quantity=10,
        )

    @mock.patch("cla_provider.helpers.ProviderAllocationHelper._get_random_provider")
    @mock.patch("cla_provider.helpers.ProviderDistributionHelper.get_distribution")
    def test_best_fit_provider_shortcut_no_cases_for_today(self, mocked_helper, mocked_random_provider_helper):
        mocked_helper.return_value = {}
        mocked_random_provider_helper.return_value = "TEST"

        ret = self.helper._get_best_fit_provider(self.category)
        self.assertTrue(mocked_helper.called)
        self.assertTrue(mocked_random_provider_helper.called)
        self.assertEqual(ret, "TEST")

    @mock.patch("cla_provider.helpers.ProviderAllocationHelper._get_random_provider")
    @mock.patch("cla_provider.helpers.ProviderDistributionHelper.get_distribution")
    def test_best_fit_provider_shortcut_current_is_ideal(self, mocked_helper, mocked_random_provider_helper):

        pd_helper = ProviderDistributionHelper(self.date)

        mocked_helper.return_value = pd_helper.make_ideal(10, self.provider_allocations)
        mocked_random_provider_helper.return_value = "TEST"

        ret = self.helper._get_best_fit_provider(self.category)
        self.assertTrue(mocked_helper.called)
        self.assertTrue(mocked_random_provider_helper.called)
        self.assertEqual(ret, "TEST")

    @mock.patch("cla_provider.helpers.ProviderAllocationHelper._get_random_provider")
    @mock.patch("cla_provider.helpers.ProviderDistributionHelper.get_distribution")
    def test_best_fit_provider_current_is_notideal_only1(self, mocked_helper, mocked_random_provider_helper):

        pd_helper = ProviderDistributionHelper(self.date)

        ideal = pd_helper.make_ideal(10, self.provider_allocations)
        ideal[ideal.keys()[0]] = 0.0

        mocked_helper.return_value = ideal
        mocked_random_provider_helper.return_value = "TEST"

        ret = self.helper._get_best_fit_provider(self.category)
        self.assertTrue(mocked_helper.called)
        self.assertFalse(mocked_random_provider_helper.called)
        self.assertNotEqual(ret, "TEST")
        self.assertEqual(ret.id, ideal.keys()[0])

    @skip("because test is flaky... waiting for Python dev to fix")
    @mock.patch("cla_provider.helpers.ProviderAllocationHelper._get_random_provider")
    @mock.patch("cla_provider.helpers.ProviderDistributionHelper.get_distribution")
    def test_best_fit_provider_current_is_notideal_2(self, mocked_helper, mocked_random_provider_helper):

        pd_helper = ProviderDistributionHelper(self.date)

        ideal = pd_helper.make_ideal(10, self.provider_allocations)
        ideal[ideal.keys()[0]] = 0.0
        ideal[ideal.keys()[1]] = 0.0

        mocked_helper.return_value = ideal
        mocked_random_provider_helper.return_value = "TEST"

        ret = self.helper._get_best_fit_provider(self.category)
        self.assertTrue(mocked_helper.called)
        mocked_random_provider_helper.assert_called_once_with(self.category, limit_choices_to=ideal.keys()[:2])
        self.assertEqual(ret, "TEST")


class ProviderDistributionHelperTestCase(TestCase):
    def setUp(self):
        self.category = make_recipe("legalaid.category")
        self.category2 = make_recipe("legalaid.category")
        self.provider_allocations = make_recipe(
            "cla_provider.provider_allocation", category=self.category, weighted_distribution=1.0, _quantity=10
        )

        self.uneven_provider_allocations = make_recipe(
            "cla_provider.provider_allocation", category=self.category, weighted_distribution=1.0, _quantity=5
        )
        self.uneven_provider_allocations.extend(
            make_recipe(
                "cla_provider.provider_allocation", category=self.category, weighted_distribution=2.0, _quantity=5
            )
        )

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
            self.assertEqual(
                len(set([v for k, v in ideal_dist.items() if k in vals])), 1
            )  # if you have the same weight then you should have the same ideal number

        return ideal_dist

    def _assign_new_case_to_provider(self, provider):
        c1 = make_recipe("legalaid.eligible_case")
        c1.diagnosis.category = self.category
        c1.assign_to_provider(provider)
        c1.diagnosis.save()
        c1.save()
        return c1

    def _pre_allocate_case_to_provider(self, provider):
        c1 = make_recipe("legalaid.eligible_case")
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
