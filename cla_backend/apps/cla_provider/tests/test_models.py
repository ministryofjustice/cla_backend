from django.test import TestCase
from django.db import IntegrityError
from core.tests.mommy_utils import make_recipe
from freezegun import freeze_time
from cla_provider.models import get_current_day_as_string


class ProviderModelTestCase(TestCase):
    provider_model = "cla_provider.provider"

    def test_unique_provider_name(self):
        make_recipe(self.provider_model, name="Stephensons")
        with self.assertRaises(IntegrityError):
            make_recipe(self.provider_model, name="Stephensons")


class TestGetCurrentDayAsString(TestCase):
    def test_full_month(self):
        week = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        # The 1st of January 2024 was a Monday
        for day in range(1, 31):
            date = "2024-01-{day}".format(day=day)
            with freeze_time(date):
                expected_day = week[(day - 1) % len(week)]
                assert get_current_day_as_string() == expected_day

    def test_leap_year(self):
        with freeze_time("2024-02-28"):
            assert get_current_day_as_string() == "wednesday"
        with freeze_time("2024-02-29"):
            assert get_current_day_as_string() == "thursday"
        with freeze_time("2024-03-01"):
            assert get_current_day_as_string() == "friday"


class WorkingDaysTestCase(TestCase):
    provider_model = "cla_provider.provider"
    provider_allocation_model = "cla_provider.provider_allocation"
    working_days_model = "cla_provider.working_days"

    def test_is_provider_working_today(self):
        provider1 = make_recipe(self.provider_model, active=True)
        provider_allocation_1 = make_recipe(self.provider_allocation_model, provider=provider1)
        make_recipe(self.working_days_model, monday=False, tuesday=True, provider_allocation=provider_allocation_1)

        with freeze_time("2024-01-08"):  # Monday the 8th of January
            assert provider_allocation_1.is_working_today() is False

        with freeze_time("2024-01-09"):  # Tuesday the 9th of January
            assert provider_allocation_1.is_working_today() is True

    def test_get_provider_working_days(self):
        provider1 = make_recipe(self.provider_model)
        provider_allocation_1 = make_recipe(self.provider_allocation_model, provider=provider1)
        make_recipe(self.working_days_model, monday=False, tuesday=True, provider_allocation=provider_allocation_1)

        assert provider_allocation_1.working_days == ["tuesday", "wednesday", "thursday", "friday"]

    def test_get_default_provider_working_days(self):
        provider1 = make_recipe(self.provider_model)
        provider_allocation_1 = make_recipe(self.provider_allocation_model, provider=provider1)
        make_recipe(self.working_days_model, provider_allocation=provider_allocation_1)

        assert provider_allocation_1.working_days == ["monday", "tuesday", "wednesday", "thursday", "friday"]

    def test_no_working_days(self):
        provider = make_recipe(self.provider_model)
        provider_allocation = make_recipe(self.provider_allocation_model, provider=provider)

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
        provider = make_recipe(self.provider_model)
        provider_allocation = make_recipe(self.provider_allocation_model, provider=provider)

        working_days = ["monday", "tuesday", "wednesday", "thursday", "friday"]
        weekend_days = ["saturday", "sunday"]

        for day in working_days:
            assert day in provider_allocation.working_days

        for day in weekend_days:
            assert day not in provider_allocation.working_days
