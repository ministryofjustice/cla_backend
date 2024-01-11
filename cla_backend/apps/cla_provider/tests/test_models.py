from django.test import TestCase
from django.db import IntegrityError
from core.tests.mommy_utils import make_recipe
from freezegun import freeze_time


class ProviderModelTestCase(TestCase):
    def test_unique_provider_name(self):
        make_recipe("cla_provider.provider", name="Stephensons")
        with self.assertRaises(IntegrityError):
            make_recipe("cla_provider.provider", name="Stephensons")


class WorkingDaysTestCase(TestCase):

    def test_is_provider_working_today(self):
        provider1 = make_recipe("cla_provider.provider", active=True)
        provider_allocation_1 = make_recipe("cla_provider.provider_allocation", provider=provider1)
        make_recipe("cla_provider.working_days", monday=False, tuesday=True, provider_allocation=provider_allocation_1)

        with freeze_time("2024-01-08"):  # Monday the 8th of January
            assert provider_allocation_1.is_working_today() is False

        with freeze_time("2024-01-09"):  # Tuesday the 9th of January
            assert provider_allocation_1.is_working_today() is True

    def test_get_provider_working_days(self):
        provider1 = make_recipe("cla_provider.provider")
        provider_allocation_1 = make_recipe("cla_provider.provider_allocation", provider=provider1)
        make_recipe("cla_provider.working_days", monday=False, tuesday=True, provider_allocation=provider_allocation_1)

        assert provider_allocation_1.working_days == ["tuesday", "wednesday", "thursday", "friday"]

    def test_get_default_provider_working_days(self):
        provider1 = make_recipe("cla_provider.provider")
        provider_allocation_1 = make_recipe("cla_provider.provider_allocation", provider=provider1)
        make_recipe("cla_provider.working_days", provider_allocation=provider_allocation_1)

        assert provider_allocation_1.working_days == ["monday", "tuesday", "wednesday", "thursday", "friday"]

    def test_no_working_days(self):
        provider = make_recipe("cla_provider.provider")
        provider_allocation = make_recipe("cla_provider.provider_allocation", provider=provider)

        with freeze_time("2024-01-08"):  # Monday the 8th of January
            assert provider_allocation.is_working_today() is True

        with freeze_time("2024-01-09"):  # Tuesday the 9th of January
            assert provider_allocation.is_working_today() is True

        with freeze_time("2024-01-10"):  # Wednesday the 10th of January
            assert provider_allocation.is_working_today() is True

        with freeze_time("2024-01-11"):  # Thursday the 11th of January
            assert provider_allocation.is_working_today() is True

        with freeze_time("2024-01-12"):  # Friday the 12th of January
            assert provider_allocation.is_working_today() is True

        with freeze_time("2024-01-13"):  # Saturday the 13th of January
            assert provider_allocation.is_working_today() is False

        with freeze_time("2024-01-14"):  # Sunday the 14th of January
            assert provider_allocation.is_working_today() is False

    def test_no_working_days_list(self):
        provider = make_recipe("cla_provider.provider")
        provider_allocation = make_recipe("cla_provider.provider_allocation", provider=provider)

        working_days = ["monday", "tuesday", "wednesday", "thursday", "friday"]
        weekend_days = ["saturday", "sunday"]

        for day in working_days:
            assert day in provider_allocation.working_days

        for day in weekend_days:
            assert day not in provider_allocation.working_days
