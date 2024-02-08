from collections import defaultdict
import datetime
from decimal import Decimal
from cla_common.call_centre_availability import on_bank_holiday

from django.test import TestCase
from django.utils import timezone
from django.conf import settings
import mock

from cla_provider.models import ProviderAllocation
from legalaid.models import Case

from core.tests.mommy_utils import make_recipe
from freezegun import freeze_time

from cla_provider.helpers import ProviderAllocationHelper, ProviderDistributionHelper


class ProviderAllocationHelperTestCase(TestCase):
    def build_providers(self, providers_data):
        providers = []
        for id, pa in providers_data.items():
            providers.append(mock.MagicMock(provider=mock.MagicMock(id=id), weighted_distribution=pa["weight"]))
        return providers

    def _test__get_random_provider(self, alloc_data, num_iterations=100000):
        # print "\n\nNew test"
        helper = ProviderAllocationHelper()
        helper._providers_in_category = self.build_providers(alloc_data)

        results = defaultdict(int)
        category = mock.MagicMock()
        for i in range(0, num_iterations):
            winner = helper._get_random_provider(category)
            results[winner.id] += 1

        for id, count in results.items():
            prob = (count * 100.0) / num_iterations
            # print 'expected %s - found %s. Difference %s' % (
            #     alloc_data[id]['expected_prob'], prob,
            #     ((alloc_data[id]['expected_prob'] * 0.01) * num_iterations) - \
            #     ((prob * 0.01) * num_iterations)
            # )
            self.assertAlmostEqual(prob, alloc_data[id]["expected_prob"], delta=1.5)

    def test__get_random_provider(self):
        # weight as integers
        self._test__get_random_provider(
            {
                20: {"weight": 20, "expected_prob": 20},
                30: {"weight": 30, "expected_prob": 30},
                50: {"weight": 50, "expected_prob": 50},
            }
        )

        # weight as floats
        self._test__get_random_provider(
            {
                28: {"weight": 2.8, "expected_prob": 28},
                27: {"weight": 2.7, "expected_prob": 27},
                4: {"weight": 0.4, "expected_prob": 4},
                5: {"weight": 0.5, "expected_prob": 5},
                13: {"weight": 1.3, "expected_prob": 13},
                1: {"weight": 0.1, "expected_prob": 1},
                10: {"weight": 1.0, "expected_prob": 10},
                12: {"weight": 1.2, "expected_prob": 12},
            }
        )

        # 2 items
        self._test__get_random_provider(
            {1: {"weight": 1, "expected_prob": 1}, 99: {"weight": 99, "expected_prob": 99}}
        )

        # # same weight
        self._test__get_random_provider(
            {
                1: {"weight": 0.8, "expected_prob": 33.3},
                2: {"weight": 0.8, "expected_prob": 33.3},
                3: {"weight": 0.8, "expected_prob": 33.3},
            }
        )

        # 0 weight
        self._test__get_random_provider(
            {0: {"weight": 0, "expected_prob": 0}, 100: {"weight": 2, "expected_prob": 100}}
        )

    @mock.patch("cla_provider.helpers.ProviderAllocation")
    def test__get_random_provider_with_empty_list(self, MockedProviderAllocation):
        MockedProviderAllocation.objects.filter.return_value = []

        helper = ProviderAllocationHelper()

        winner = helper._get_random_provider(mock.MagicMock())
        self.assertEqual(winner, None)

    def test_get_qualifying_providers(self):
        category1 = make_recipe("legalaid.category")
        category2 = make_recipe("legalaid.category")

        cat1_provider1 = make_recipe("cla_provider.provider", active=True)
        make_recipe(
            "cla_provider.provider_allocation", weighted_distribution=0.5, provider=cat1_provider1, category=category1
        )

        cat1_provider2 = make_recipe("cla_provider.provider", active=True)
        make_recipe(
            "cla_provider.provider_allocation", weighted_distribution=0.5, provider=cat1_provider2, category=category1
        )

        cat2_provider1 = make_recipe("cla_provider.provider", active=True)
        make_recipe(
            "cla_provider.provider_allocation", weighted_distribution=0.5, provider=cat2_provider1, category=category2
        )

        helper = ProviderAllocationHelper()
        cat1_providers = helper.get_qualifying_providers(category1)
        self.assertItemsEqual(cat1_providers, [cat1_provider1, cat1_provider2])

        # Set cat1_provider2.active == False => only one prov returned
        cat1_provider2.active = False
        cat1_provider2.save()

        helper = ProviderAllocationHelper()
        cat1_providers = helper.get_qualifying_providers(category1)
        self.assertItemsEqual(cat1_providers, [cat1_provider1])

    def test_get_suggested_provider_random(self):

        as_of = timezone.make_aware(
            datetime.datetime(day=8, month=12, year=2014, hour=10, minute=0), timezone.get_current_timezone()
        )

        category = make_recipe("legalaid.category")

        provider = make_recipe("cla_provider.provider", active=True)
        make_recipe(
            "cla_provider.provider_allocation", weighted_distribution=0.5, provider=provider, category=category
        )

        helper = ProviderAllocationHelper(as_of=as_of)
        choosen_provider = helper._get_random_provider(category)
        self.assertEqual(choosen_provider, provider)

        # Set cat1_provider2.active == False => only one prov returned
        provider.active = False
        provider.save()

        helper = ProviderAllocationHelper(as_of=as_of)
        choosen_provider = helper.get_suggested_provider(category)
        self.assertEqual(choosen_provider, None)

    # This @mock.patch ensures that all settings.NON_ROTA_OPENING_HOURS checks always return True. This should not
    # impact the test logic as this test is only checking provider allocation distribution
    @mock.patch("cla_common.call_centre_availability.OpeningHours.available", return_value=True)
    def test_get_suggested_provider_best_fit(self, mock_openingHours_available):
        # slightly brute force test

        as_of = timezone.make_aware(
            datetime.datetime(day=8, month=12, year=2014, hour=10, minute=0), timezone.get_current_timezone()
        )

        category = make_recipe("legalaid.category")

        provider1 = make_recipe("cla_provider.provider", active=True)
        provider2 = make_recipe("cla_provider.provider", active=True)
        make_recipe(
            "cla_provider.provider_allocation", weighted_distribution=0.5, provider=provider1, category=category
        )
        make_recipe("cla_provider.provider_allocation", weighted_distribution=1, provider=provider2, category=category)
        ProviderAllocation.objects.update(modified=as_of - datetime.timedelta(days=1))

        helper = ProviderAllocationHelper(as_of=as_of)
        counts = {provider1: 0, provider2: 0}
        # quick sanity check that random allocation is working
        for i in range(100):
            sugg = helper.get_suggested_provider(category)
            counts[sugg] += 1
        self.assertTrue(counts[provider2] > counts[provider1])

        case1 = make_recipe("legalaid.eligible_case", diagnosis__category=category)
        case1.assign_to_provider(provider1)

        # cases assigned at != today are ignored, so expect same as before
        counts = {provider1: 0, provider2: 0}
        for i in range(100):
            sugg = helper.get_suggested_provider(category)
            counts[sugg] += 1
        self.assertTrue(counts[provider2] > counts[provider1])

        case1.provider_assigned_at = as_of
        case1.save()

        for i in range(100):
            self.assertEqual(helper.get_suggested_provider(category), provider2)
            # should always be provider 2

    def test_get_suggested_provider_rota(self):
        as_of = timezone.make_aware(
            datetime.datetime(day=7, month=12, year=2014, hour=10, minute=0), timezone.get_current_timezone()
        )

        category = make_recipe("legalaid.category")

        provider = make_recipe("cla_provider.provider", active=True)
        make_recipe(
            "cla_provider.outofhoursrota",
            provider=provider,
            start_date=as_of,
            end_date=as_of + datetime.timedelta(days=1),
            category=category,
        )

        helper = ProviderAllocationHelper(as_of=as_of)
        choosen_provider = helper.get_suggested_provider(category)
        self.assertEqual(choosen_provider, provider)

        # Set cat1_provider2.active == False => only one prov returned
        provider.active = False
        provider.save()

        helper = ProviderAllocationHelper(as_of=as_of)
        choosen_provider = helper.get_suggested_provider(category)
        self.assertEqual(choosen_provider, None)

    def assertWithinAllowedAccuracy(self, expected, accuracy, n):
        diff = expected * accuracy
        if not expected - diff <= n <= expected + diff:
            raise self.failureException(
                "Expected: %s, Got: %s  - not within allowed accuracy: %s" % (expected, n, accuracy)
            )

    # This @mock.patch ensures that all settings.NON_ROTA_OPENING_HOURS checks always return True. This should not
    # impact the test logic as this test is only checking provider allocation distribution
    @mock.patch("cla_common.call_centre_availability.OpeningHours.available", return_value=True)
    def test_even_distribution(self, mock_openinghours_available):
        # Test the distribution of cases to {accuracy} accuracy over {total} cases
        total = 80
        accuracy = Decimal("0.001")
        with mock.patch(
            "cla_common.call_centre_availability.current_datetime", datetime.datetime(2015, 7, 7, 11, 59, 0)
        ):
            helper = ProviderAllocationHelper()

            as_of = timezone.make_aware(
                datetime.datetime(day=7, month=7, year=2015, hour=12, minute=0), timezone.get_current_timezone()
            )

            category = make_recipe("legalaid.category")

            provider1 = make_recipe("cla_provider.provider", active=True)
            provider2 = make_recipe("cla_provider.provider", active=True)
            provider3 = make_recipe("cla_provider.provider", active=True)
            provider4 = make_recipe("cla_provider.provider", active=True)
            make_recipe(
                "cla_provider.provider_allocation", weighted_distribution=5, provider=provider1, category=category
            )
            make_recipe(
                "cla_provider.provider_allocation", weighted_distribution=1, provider=provider2, category=category
            )
            make_recipe(
                "cla_provider.provider_allocation", weighted_distribution=1, provider=provider3, category=category
            )
            make_recipe(
                "cla_provider.provider_allocation", weighted_distribution=1, provider=provider4, category=category
            )
            ProviderAllocation.objects.update(modified=as_of - datetime.timedelta(days=1))

            ec = make_recipe("legalaid.eligibility_check_yes", category=category, _quantity=total)

            for n, e in enumerate(ec):
                d = make_recipe("diagnosis.diagnosis_yes", category=category)
                c = make_recipe("legalaid.eligible_case", id=n + 1, eligibility_check=e, diagnosis=d)
                p = helper.get_suggested_provider(category)
                c.assign_to_provider(p)

            self.assertEqual(Case.objects.all().count(), total)

            self.assertWithinAllowedAccuracy(50, accuracy, provider1.case_set.count())
            self.assertWithinAllowedAccuracy(10, accuracy, provider2.case_set.count())
            self.assertWithinAllowedAccuracy(10, accuracy, provider3.case_set.count())
            self.assertWithinAllowedAccuracy(10, accuracy, provider4.case_set.count())

    # This @mock.patch ensures that all settings.NON_ROTA_OPENING_HOURS checks always return True. This should not
    # impact the test logic as this test is only checking provider allocation distribution
    @mock.patch("cla_common.call_centre_availability.OpeningHours.available", return_value=True)
    def test_get_distribution(self, mock_openinghours_available):
        with mock.patch(
            "cla_common.call_centre_availability.current_datetime", datetime.datetime(2015, 7, 7, 11, 59, 0)
        ):
            as_of = timezone.make_aware(
                datetime.datetime(day=7, month=7, year=2015, hour=12, minute=0), timezone.get_current_timezone()
            )
            distribution_helper = ProviderDistributionHelper(as_of)

            category = make_recipe("legalaid.category")

            provider1 = make_recipe("cla_provider.provider", active=True)
            provider2 = make_recipe("cla_provider.provider", active=True)
            provider3 = make_recipe("cla_provider.provider", active=True)
            make_recipe(
                "cla_provider.provider_allocation", weighted_distribution=1, provider=provider1, category=category
            )
            make_recipe(
                "cla_provider.provider_allocation", weighted_distribution=1, provider=provider2, category=category
            )
            make_recipe(
                "cla_provider.provider_allocation", weighted_distribution=1, provider=provider3, category=category
            )

            ec = make_recipe("legalaid.eligibility_check_yes", category=category, _quantity=12)

            for i in range(1, 6):
                d = make_recipe("diagnosis.diagnosis_yes", category=category)
                c = make_recipe("legalaid.eligible_case", id=i, eligibility_check=ec[i], diagnosis=d)
                c.assign_to_provider(provider1)

            for i in range(7, 9):
                d = make_recipe("diagnosis.diagnosis_yes", category=category)
                c = make_recipe("legalaid.eligible_case", id=i, eligibility_check=ec[i], diagnosis=d)
                c.assign_to_provider(provider2)

            for i in range(9, 10):
                d = make_recipe("diagnosis.diagnosis_yes", category=category)
                c = make_recipe("legalaid.eligible_case", id=i, eligibility_check=ec[i], diagnosis=d)
                c.assign_to_provider(provider3)

            self.assertDictEqual(
                distribution_helper.get_distribution(category), {provider1.pk: 5, provider2.pk: 2, provider3.pk: 1}
            )

    def test_distribution_with_rota(self):
        with mock.patch(
            "cla_common.call_centre_availability.current_datetime", datetime.datetime(2015, 7, 7, 11, 59, 0)
        ):
            as_of = timezone.make_aware(
                datetime.datetime(day=7, month=7, year=2015, hour=12, minute=0), timezone.get_current_timezone()
            )
            distribution_helper = ProviderDistributionHelper(as_of)

            category = make_recipe("legalaid.category")

            provider1 = make_recipe("cla_provider.provider", active=True)
            provider2 = make_recipe("cla_provider.provider", active=True)
            aloc1 = make_recipe(
                "cla_provider.provider_allocation",
                weighted_distribution=1,
                provider=provider1,
                category=category,
                modified=as_of,
            )
            aloc1.modified = as_of
            aloc1.save()

            aloc2 = make_recipe(
                "cla_provider.provider_allocation",
                weighted_distribution=1,
                provider=provider2,
                category=category,
                modified=as_of,
            )
            aloc2.modified = as_of
            aloc2.save()

            d = make_recipe("diagnosis.diagnosis_yes", id=1, category=category)

            ec = make_recipe("legalaid.eligibility_check_yes", id=1, category=category)

            c = make_recipe("legalaid.eligible_case", id=1, eligibility_check=ec, diagnosis=d)

            tz = timezone.now().replace(hour=20, minute=59)
            tz = tz + datetime.timedelta(days=7 - tz.weekday())
            while on_bank_holiday(tz):
                tz = tz + datetime.timedelta(days=7 - tz.weekday())

            with mock.patch("django.utils.timezone.now", lambda: tz):
                c.assign_to_provider(provider1)

            self.assertDictEqual(distribution_helper.get_distribution(category), {})

            d2 = make_recipe("diagnosis.diagnosis_yes", id=2, category=category)

            ec2 = make_recipe("legalaid.eligibility_check_yes", id=2, category=category)

            c2 = make_recipe("legalaid.eligible_case", id=2, eligibility_check=ec2, diagnosis=d2)

            tz2 = timezone.now().replace(hour=11, minute=59)
            tz2 = tz2 + datetime.timedelta(days=7 - tz2.weekday())
            while on_bank_holiday(tz2):
                tz2 = tz2 + datetime.timedelta(days=7 - tz2.weekday())

            with mock.patch("django.utils.timezone.now", lambda: tz2):
                # Make sure this case is assigned to a provider within business hours.
                # Otherwise this test will fail when tz falls out of business hours
                with mock.patch("cla_common.call_centre_availability.OpeningHours.available", return_value=True):
                    c2.assign_to_provider(provider2)

            self.assertDictEqual(distribution_helper.get_distribution(category), {provider2.pk: 1})

    @mock.patch("cla_common.call_centre_availability.OpeningHours.available", return_value=True)
    def test_allocation_resets_when_weighting_changes(self, mock_openinghours_available):
        base_datetime = timezone.make_aware(
            datetime.datetime(day=7, month=7, year=2015, hour=12, minute=0), timezone.get_current_timezone()
        )
        category = make_recipe("legalaid.category")

        provider1 = make_recipe("cla_provider.provider", active=True)
        provider2 = make_recipe("cla_provider.provider", active=True)
        make_recipe("cla_provider.provider_allocation", weighted_distribution=1, provider=provider1, category=category)
        make_recipe("cla_provider.provider_allocation", weighted_distribution=1, provider=provider2, category=category)
        ProviderAllocation.objects.update(modified=base_datetime - datetime.timedelta(days=30))

        existing_eligibility_checks = make_recipe("legalaid.eligibility_check_yes", category=category, _quantity=50)
        new_eligibility_checks = make_recipe("legalaid.eligibility_check_yes", category=category, _quantity=50)

        with mock.patch("cla_common.call_centre_availability.current_datetime", base_datetime), mock.patch(
            "legalaid.models.timezone.now", return_value=base_datetime
        ):
            for e in existing_eligibility_checks:
                as_of = base_datetime
                helper = ProviderAllocationHelper(as_of)
                d = make_recipe("diagnosis.diagnosis_yes", category=category)
                c = make_recipe("legalaid.eligible_case", eligibility_check=e, diagnosis=d)
                c.assign_to_provider(provider1)

        self.assertEqual(provider1.case_set.count(), 50)
        self.assertEqual(provider2.case_set.count(), 0)

        new_datetime = base_datetime + datetime.timedelta(days=1)
        ProviderAllocation.objects.update(modified=new_datetime)
        with mock.patch("cla_common.call_centre_availability.current_datetime", new_datetime), mock.patch(
            "legalaid.models.timezone.now", return_value=new_datetime
        ):
            for e in new_eligibility_checks:
                as_of = new_datetime
                helper = ProviderAllocationHelper(as_of)
                d = make_recipe("diagnosis.diagnosis_yes", category=category)
                c = make_recipe("legalaid.eligible_case", eligibility_check=e, diagnosis=d)
                p = helper.get_suggested_provider(category)
                c.assign_to_provider(p)

        self.assertEqual(provider1.case_set.count(), 75)
        self.assertEqual(provider2.case_set.count(), 25)

    @mock.patch("cla_common.call_centre_availability.OpeningHours.available", return_value=True)
    def test_allocation_with_low_volume_per_day(self, mock_openinghours_available):
        base_datetime = timezone.make_aware(
            datetime.datetime(day=7, month=7, year=2015, hour=12, minute=0), timezone.get_current_timezone()
        )
        category = make_recipe("legalaid.category")

        provider1 = make_recipe("cla_provider.provider", active=True)
        provider2 = make_recipe("cla_provider.provider", active=True)
        make_recipe("cla_provider.provider_allocation", weighted_distribution=1, provider=provider1, category=category)
        make_recipe("cla_provider.provider_allocation", weighted_distribution=1, provider=provider2, category=category)
        ProviderAllocation.objects.update(modified=base_datetime - datetime.timedelta(days=30))

        eligibility_checks = make_recipe("legalaid.eligibility_check_yes", category=category, _quantity=30)

        for i, e in enumerate(eligibility_checks):
            as_of = base_datetime + datetime.timedelta(days=i)
            with mock.patch("cla_common.call_centre_availability.current_datetime", base_datetime), mock.patch(
                "legalaid.models.timezone.now", return_value=as_of
            ):
                helper = ProviderAllocationHelper(as_of)
                d = make_recipe("diagnosis.diagnosis_yes", category=category)
                c = make_recipe("legalaid.eligible_case", eligibility_check=e, diagnosis=d)
                p = helper.get_suggested_provider(category)
                c.assign_to_provider(p)

        self.assertEqual(provider1.case_set.count(), provider2.case_set.count())


class TestIsProviderUnderCapacity(TestCase):
    provider_allocation_model = "cla_provider.provider_allocation"

    def setUp(self):
        self.helper = ProviderAllocationHelper()
        self.provider = make_recipe("cla_provider.provider", active=True, id=1)

    test_case_0 = {2: 1}

    @mock.patch("cla_provider.helpers.ProviderDistributionHelper.get_distribution", return_value=test_case_0)
    def test_no_current_allocation(self, _):
        self.provider_allocation = make_recipe(
            self.provider_allocation_model, weighted_distribution=1, provider=self.provider
        )
        assert self.helper.is_provider_under_capacity(self.provider_allocation) is True

    test_case_1 = {1: 1, 2: 1}

    @mock.patch("cla_provider.helpers.ProviderDistributionHelper.get_distribution", return_value=test_case_1)
    def test_at_full_capacity(self, _):
        provider_allocation = make_recipe(
            self.provider_allocation_model, weighted_distribution=0.5, provider=self.provider
        )
        assert self.helper.is_provider_under_capacity(provider_allocation) is True

    test_case_2 = {1: 5, 2: 2}

    @mock.patch("cla_provider.helpers.ProviderDistributionHelper.get_distribution", return_value=test_case_2)
    def test_above_capacity(self, _):
        provider_allocation = make_recipe(
            self.provider_allocation_model, weighted_distribution=0.5, provider=self.provider
        )
        assert self.helper.is_provider_under_capacity(provider_allocation) is False

    test_case_3 = {1: 2, 2: 5}

    @mock.patch("cla_provider.helpers.ProviderDistributionHelper.get_distribution", return_value=test_case_3)
    def test_below_capacity(self, _):
        provider_allocation = make_recipe(
            self.provider_allocation_model, weighted_distribution=0.6, provider=self.provider
        )
        assert self.helper.is_provider_under_capacity(provider_allocation) is True

    test_case_4 = {}

    @mock.patch("cla_provider.helpers.ProviderDistributionHelper.get_distribution", return_value=test_case_4)
    def test_blank_distribution(self, _):
        provider_allocation = make_recipe(
            self.provider_allocation_object, weighted_distribution=0.1, provider=self.provider
        )
        assert self.helper.is_provider_under_capacity(provider_allocation) is True

    test_case_5 = {1: 1000, 2: 5000, 51: 4000, 64: 10000}

    @mock.patch("cla_provider.helpers.ProviderDistributionHelper.get_distribution", return_value=test_case_5)
    def test_larger_sample_size(self, _):
        provider_allocation = make_recipe(
            self.provider_allocation_object, weighted_distribution=0.051, provider=self.provider
        )
        assert self.helper.is_provider_under_capacity(provider_allocation) is True


class TestEducationAllocationCalled(TestCase):
    def setUp(self):
        self.education_category = make_recipe("legalaid.category", code="education")

    @mock.patch("cla_provider.helpers.ProviderAllocationHelper.get_valid_education_provider_allocations")
    def test_education_category(self, get_valid_education_provider_allocations):
        settings.EDUCATION_ALLOCATION_FEATURE_FLAG = True
        helper = ProviderAllocationHelper()
        helper.get_qualifying_providers_allocation(self.education_category)

        assert get_valid_education_provider_allocations.called, "get_valid_education_provider_allocations was not called"

    @mock.patch("cla_provider.helpers.ProviderAllocationHelper.get_valid_education_provider_allocations")
    def test_not_education_category(self, get_valid_education_provider_allocations):
        settings.EDUCATION_ALLOCATION_FEATURE_FLAG = True
        helper = ProviderAllocationHelper()
        helper.get_qualifying_providers_allocation(self.education_category)

        assert not get_valid_education_provider_allocations.called, "get_valid_education_provider_allocations was called"


class TestEducationAllocationFeatureFlag(TestCase):
    def setUp(self):
        self.education_category = make_recipe("legalaid.category", code="education")

    @mock.patch("cla_provider.helpers.ProviderAllocationHelper.get_valid_education_provider_allocations")
    def test_feature_flag_enabled(self, get_valid_education_provider_allocations):
        settings.EDUCATION_ALLOCATION_FEATURE_FLAG = True
        helper = ProviderAllocationHelper()
        helper.get_qualifying_providers_allocation(self.education_category)

        assert get_valid_education_provider_allocations.called, "get_valid_education_provider_allocations was not called"

    @mock.patch("cla_provider.helpers.ProviderAllocationHelper.get_valid_education_provider_allocations")
    def test_feature_flag_disabled(self, get_valid_education_provider_allocations):
        settings.EDUCATION_ALLOCATION_FEATURE_FLAG = False
        helper = ProviderAllocationHelper()
        helper.get_qualifying_providers_allocation(self.education_category)

        assert not get_valid_education_provider_allocations.called, "get_valid_education_provider_allocations was called"


class TestGetValidEducationProviders(TestCase):
    working_days_model = "cla_provider.working_days"
    provider_allocation_model = "cla_provider.provider_allocation"
    helper = ProviderAllocationHelper()
    provider_model = "cla_provider.provider"

    def setUp(self):
        self.education_category = make_recipe("legalaid.category", code="education")

    def test_no_providers(self):
        provider_allocations = self.helper.get_valid_education_provider_allocations(self.education_category)

        assert provider_allocations == []

    def test_one_providers(self):
        provider = make_recipe(self.provider_model, active=True)
        provider_allocation = make_recipe(
            self.provider_allocation_model, provider=provider, category=self.education_category
        )

        actual_output = self.helper.get_valid_education_provider_allocations(self.education_category)

        assert actual_output == [provider_allocation], actual_output

    def test_two_providers(self):
        provider_allocations = []
        for id in range(2):
            provider = make_recipe(self.provider_model, active=True, id=id)
            provider_allocations.append(
                make_recipe(self.provider_allocation_model, provider=provider, category=self.education_category)
            )

        actual_output = self.helper.get_valid_education_provider_allocations(self.education_category)

        assert actual_output == provider_allocations, actual_output

    def test_provider_not_working(self):
        provider = make_recipe(self.provider_model, active=True)

        provider_allocation = make_recipe(
            self.provider_allocation_model, provider=provider, category=self.education_category
        )

        make_recipe(self.working_days_model, monday=False, provider_allocation=provider_allocation)

        # This is a Monday so we should expect the provider to be invalid.
        with freeze_time("2024-01-01"):
            actual_output = self.helper.get_valid_education_provider_allocations(self.education_category)

        assert actual_output == [], actual_output

    def test_some_providers_working(self):
        provider_1 = make_recipe(self.provider_model, active=True, id=1)
        provider_2 = make_recipe(self.provider_model, active=True, id=2)

        provider_allocation_1 = make_recipe(
            self.provider_allocation_model, provider=provider_1, category=self.education_category
        )
        provider_allocation_2 = make_recipe(
            self.provider_allocation_model, provider=provider_2, category=self.education_category
        )

        make_recipe(self.working_days_model, monday=False, provider_allocation=provider_allocation_1)
        make_recipe(self.working_days_model, monday=True, provider_allocation=provider_allocation_2)

        # This is a Monday so we should expect the provider to be invalid.
        with freeze_time("2024-01-01"):
            actual_output = self.helper.get_valid_education_provider_allocations(self.education_category)

        assert actual_output == [provider_allocation_2], actual_output

    provider_distribution_1 = {
        1: 2,
        2: 0,
    }  # This is a distribution where provider 1 is assigned 100% of the total cases.
    provider_distribution_2 = {
        1: 2,
        2: 2,
    }  # This is a distribution where provider 1 is assigned 50% of the total cases.

    @mock.patch(
        "cla_provider.helpers.ProviderDistributionHelper.get_distribution", return_value=provider_distribution_1
    )
    def test_provider_over_capacity_on_a_thursday(self, _):
        """ If a provider is over capacity on a Thursday then the case should go to face to face.
        In this situation, the provider is invalid and the operator will manually assign the case.
        """
        provider = make_recipe(self.provider_model, active=True, id=1)

        provider_allocation = make_recipe(
            self.provider_allocation_model,
            provider=provider,
            weighted_distribution=0.6,
            category=self.education_category,
        )

        # Check they are over their capacity
        assert not self.helper.is_provider_under_capacity(provider_allocation)

        # This is a Thursday
        with freeze_time("2024-01-04"):
            actual_output = self.helper.get_valid_education_provider_allocations(self.education_category)

        assert actual_output == [], actual_output

    @mock.patch(
        "cla_provider.helpers.ProviderDistributionHelper.get_distribution", return_value=provider_distribution_2
    )
    def test_provider_under_capacity_on_a_thursday(self, _):
        """ If a provider is over capacity on a Thursday then the case should go to face to face.
        In this situation, the provider is invalid and the operator will manually assign the case.
        """
        provider = make_recipe(self.provider_model, active=True, id=1)

        provider_allocation = make_recipe(
            "cla_provider.provider_allocation",
            provider=provider,
            weighted_distribution=0.6,
            category=self.education_category,
        )

        # Check they are over their capacity
        assert self.helper.is_provider_under_capacity(provider_allocation)

        # This is a Thursday
        with freeze_time("2024-01-04"):
            actual_output = self.helper.get_valid_education_provider_allocations(self.education_category)

        assert actual_output == [provider_allocation], actual_output

    @mock.patch(
        "cla_provider.helpers.ProviderDistributionHelper.get_distribution", return_value=provider_distribution_1
    )
    def test_provider_over_capacity_on_a_wednesday(self, _):
        """ If a provider is over capacity on a Wednesday they should still be a valid provider.
        """
        provider = make_recipe("cla_provider.provider", active=True, id=1)

        provider_allocation = make_recipe(
            self.provider_allocation_model,
            provider=provider,
            weighted_distribution=0.6,
            category=self.education_category,
        )

        # Check they are over their capacity
        assert not self.helper.is_provider_under_capacity(provider_allocation)

        # This is a Wednesday
        with freeze_time("2024-01-03"):
            actual_output = self.helper.get_valid_education_provider_allocations(self.education_category)

        assert actual_output == [provider_allocation], actual_output

    provider_distribution = {1: 2, 2: 2}  # This is a distribution where provider 1 is assigned 50% of the total cases.


class TestGetCasesAssignedToCode(TestCase):
    helper = ProviderDistributionHelper()
    case_model = "legalaid.case"
    date_format = "%d %B, %Y"

    def test_manref_today(self):
        now = datetime.datetime.now()
        case = make_recipe(self.case_model, outcome_code="MANREF", modified=now)
        assert case in self.helper.get_cases_assigned_to_code("MANREF", now.date)

    def test_multiple_edff(self):
        cases = []
        for day in range(1, 31):
            now = datetime.datetime.strptime("%d January, 2024" % day, self.date_format)
            cases.append(make_recipe(self.case_model, outcome_code="EDFF", modified=now))

        assert len(cases) == len(self.helper.get_cases_assigned_to_code("EDFF", datetime.datetime.strptime("1 January, 2024", self.date_format))) == 30

    def test_multiple_outcome_codes(self):
        outcome_codes = ["MANREF", "SPFM", "EDFF", "SPOR"]
        cases = []
        for day in range(1, 31):
            now = datetime.datetime.strptime("%d January, 2024" % day, self.date_format)
            outcome_code = outcome_codes[day % len(outcome_codes)]  # Iterate across the list of possible outcome codes
            cases.append(make_recipe('legalaid.case', outcome_code=outcome_code, modified=now))

        assert 8 == len(self.helper.get_cases_assigned_to_code("SPFM", datetime.datetime.strptime("1 January, 2024", self.date_format)))


class TestProviderAllocationDifferenceVsIdeal(TestCase):
    provider_model = "cla_provider.provider"
    provider_allocation_model = "cla_provider.provider_allocation"

    @staticmethod
    def isFloatClose(float1, float2):
        return abs(float1 - float2) < 0.001

    def setUp(self):
        self.helper = ProviderAllocationHelper()

    def test_empty_distribution(self):
        provider_allocation = make_recipe(self.provider_allocation_model, weighted_distribution=0.5)
        assert self.helper._get_provider_allocation_difference_vs_ideal(provider_allocation, {}) == 0

    def test_no_weighting(self):
        provider = make_recipe(self.provider_model, id=1)
        provider_allocation = make_recipe(self.provider_allocation_model, weighted_distribution=0, provider=provider)
        distribution = {2: 19, 3: 36}
        assert self.helper._get_provider_allocation_difference_vs_ideal(provider_allocation, distribution) == 0

    def test_simple_distribution(self):
        provider = make_recipe(self.provider_model, id=1)
        provider_allocation = make_recipe(self.provider_allocation_model, provider=provider, weighted_distribution=0.5)
        distribution = {provider.id: 4}
        assert self.helper._get_provider_allocation_difference_vs_ideal(provider_allocation, distribution) == -2

    def test_over_allocated_distribution(self):
        provider = make_recipe(self.provider_model, id=1)
        provider_allocation = make_recipe(self.provider_allocation_model, provider=provider, weighted_distribution=0.5)
        distribution = {provider.id: 10}
        assert self.helper._get_provider_allocation_difference_vs_ideal(provider_allocation, distribution) == -5

    def test_not_in_distribution(self):
        provider = make_recipe(self.provider_model, id=1)
        provider_2 = make_recipe(self.provider_model, id=2)
        provider_allocation = make_recipe(self.provider_allocation_model, provider=provider, weighted_distribution=0.5)
        distribution = {provider_2.id: 10}
        assert self.helper._get_provider_allocation_difference_vs_ideal(provider_allocation, distribution) == 5

    def test_standard_distribution(self):
        provider_1 = make_recipe(self.provider_model, id=1)
        provider_2 = make_recipe(self.provider_model, id=2)
        provider_allocation_1 = make_recipe(self.provider_allocation_model, provider=provider_1, weighted_distribution=0.6)
        provider_allocation_2 = make_recipe(self.provider_allocation_model, provider=provider_2, weighted_distribution=0.2)
        distribution = {provider_1.id: 4, provider_2.id: 10}
        assert self.isFloatClose(self.helper._get_provider_allocation_difference_vs_ideal(provider_allocation_1, distribution), 4.4)
        assert self.isFloatClose(self.helper._get_provider_allocation_difference_vs_ideal(provider_allocation_2, distribution), -7.2)

    def test_edff_distribution(self):
        provider_1 = make_recipe(self.provider_model, id=1)
        provider_2 = make_recipe(self.provider_model, id=2)
        provider_allocation_1 = make_recipe(self.provider_allocation_model, provider=provider_1, weighted_distribution=0.6)
        provider_allocation_2 = make_recipe(self.provider_allocation_model, provider=provider_2, weighted_distribution=0.2)
        distribution = {provider_1.id: 4, provider_2.id: 10, "EDFF": 10}
        assert self.isFloatClose(self.helper._get_provider_allocation_difference_vs_ideal(provider_allocation_1, distribution), 10.4)
        assert self.isFloatClose(self.helper._get_provider_allocation_difference_vs_ideal(provider_allocation_2, distribution), -5.2)


class TestGetBestFitEducationProvider(TestCase):
    helper = ProviderAllocationHelper()
    provider_model = "cla_provider.provider"
    provider_allocation_model = "cla_provider.provider_allocation"

    def setUp(self):
        self.education_category = make_recipe("legalaid.category", code="education")

    provider_distribution_1 = {1: 0, 2: 10}

    @mock.patch(
        "cla_provider.helpers.ProviderDistributionHelper.get_distribution", return_value=provider_distribution_1
    )
    def test_standard_distribution(self, _):
        provider_1 = make_recipe(self.provider_model, id=1, active=True)
        provider_2 = make_recipe(self.provider_model, id=2, active=True)

        make_recipe(self.provider_allocation_model, provider=provider_1, weighted_distribution=0.5, category=self.education_category)
        make_recipe(self.provider_allocation_model, provider=provider_2, weighted_distribution=0.2, category=self.education_category)

        # This is a Wednesday
        with freeze_time("2024-01-03"):
            assert self.helper.get_best_fit_education_provider(self.education_category).id == provider_1.id

    provider_distribution_2 = {1: 4, 2: 0}

    @mock.patch(
        "cla_provider.helpers.ProviderDistributionHelper.get_distribution", return_value=provider_distribution_2
    )
    def test_standard_distribution_2(self, _):
        provider_1 = make_recipe(self.provider_model, id=1, active=True)
        provider_2 = make_recipe(self.provider_model, id=2, active=True)

        make_recipe(self.provider_allocation_model, provider=provider_1, weighted_distribution=0, category=self.education_category)
        make_recipe(self.provider_allocation_model, provider=provider_2, weighted_distribution=0.5, category=self.education_category)

        # This is a Wednesday
        with freeze_time("2024-01-03"):
            assert self.helper.get_best_fit_education_provider(self.education_category).id == provider_2.id

    provider_distribution_3 = {1: 10, 2: 10}

    @mock.patch(
        "cla_provider.helpers.ProviderDistributionHelper.get_distribution", return_value=provider_distribution_3
    )
    def test_standard_distribution_3(self, _):
        provider_1 = make_recipe(self.provider_model, id=1, active=True)
        provider_2 = make_recipe(self.provider_model, id=2, active=True)

        make_recipe(self.provider_allocation_model, provider=provider_1, weighted_distribution=0.2, category=self.education_category)
        make_recipe(self.provider_allocation_model, provider=provider_2, weighted_distribution=0.6, category=self.education_category)

        # This is a Wednesday
        with freeze_time("2024-01-03"):
            assert self.helper.get_best_fit_education_provider(self.education_category).id == provider_2.id

    @mock.patch(
        "cla_provider.helpers.ProviderDistributionHelper.get_distribution", return_value=provider_distribution_3
    )
    def test_edff_distribution(self, _):
        provider_1 = make_recipe(self.provider_model, id=1, active=True)
        provider_2 = make_recipe(self.provider_model, id=2, active=True)

        for _ in range(99):
            make_recipe('legalaid.case', outcome_code="EDFF", modified=datetime.datetime.now())

        make_recipe('cla_provider.provider_allocation', provider=provider_1, weighted_distribution=0.2, category=self.education_category)
        make_recipe('cla_provider.provider_allocation', provider=provider_2, weighted_distribution=0.6, category=self.education_category)

        # This is a Wednesday
        with freeze_time("2024-01-03"):
            assert self.helper.get_best_fit_education_provider(self.education_category).id == provider_2.id
