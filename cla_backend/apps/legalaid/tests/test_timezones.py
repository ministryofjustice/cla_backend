import pytz
from django.core.management import call_command, CommandError
from django.test import TestCase
from django.utils import timezone
from django.utils.six import StringIO
from freezegun import freeze_time

from core.tests.mommy_utils import make_recipe
from legalaid.models import Case


class BaseAssignedOutOfHours(object):
    def tearDown(self):
        self.freezer.stop()
        super(BaseAssignedOutOfHours, self).tearDown()

    def create_and_assign(self, dt):
        timezone_aware_dt = timezone.make_aware(dt, timezone.get_current_timezone())
        utc_dt = timezone_aware_dt.astimezone(pytz.utc)
        self.freezer = freeze_time(utc_dt)
        self.freezer.start()
        provider = make_recipe("cla_provider.provider")
        case = make_recipe("legalaid.case")
        case.assign_to_provider(provider)
        return case

    def test_before_hours(self):
        case = self.create_and_assign(self.dt.replace(hour=7, minute=30))
        self.assertTrue(case.assigned_out_of_hours)
        return case

    def test_first_hour_of_business(self):
        case = self.create_and_assign(self.dt.replace(hour=8, minute=30))
        self.assertFalse(case.assigned_out_of_hours)

    def test_second_hour_of_business(self):
        case = self.create_and_assign(self.dt.replace(hour=9, minute=30))
        self.assertFalse(case.assigned_out_of_hours)

    def test_last_hour_of_business(self):
        case = self.create_and_assign(self.dt.replace(hour=16, minute=30))
        self.assertFalse(case.assigned_out_of_hours)

    def test_after_hours(self):
        case = self.create_and_assign(self.dt.replace(hour=17, minute=30))
        self.assertTrue(case.assigned_out_of_hours)


class TestGMTAssignedOutOfHoursTestCase(BaseAssignedOutOfHours, TestCase):
    dt = timezone.datetime(2021, 2, 2)


class TestBSTAssignedOutOfHoursTestCase(BaseAssignedOutOfHours, TestCase):
    dt = timezone.datetime(2021, 5, 5)


class TestCommandDateArgument(TestCase):
    def test_requires_date(self):
        with self.assertRaisesMessage(CommandError, "A start date is required"):
            call_command("recalculate_assigned_out_of_hours")

    def test_date_must_be_a_date_string(self):
        with self.assertRaisesMessage(CommandError, "The start date should be a valid datetime in yyyy-mm-dd format"):
            call_command("recalculate_assigned_out_of_hours", "last year")

    def test_date_must_be_correctly_formatted(self):
        with self.assertRaisesMessage(CommandError, "The start date should be a valid datetime in yyyy-mm-dd format"):
            call_command("recalculate_assigned_out_of_hours", "2021-30-06")

    def test_date_must_be_valid(self):
        with self.assertRaisesMessage(CommandError, "The start date should be a valid datetime in yyyy-mm-dd format"):
            call_command("recalculate_assigned_out_of_hours", "2021-02-30")


class TestRecalculateAssignedOutOfHours(TestCase):
    dt = "2020-04-01"

    def setUp(self, *args, **kwargs):
        self.provider = make_recipe("cla_provider.provider")
        self.category = make_recipe("legalaid.category", code="education")
        super(TestRecalculateAssignedOutOfHours, self).setUp()

    def create(self, year, month, day, hour, minute, out_of_hours):
        assigned_at = timezone.datetime(year, month, day, hour, minute)
        case = make_recipe(
            "legalaid.case",
            provider_assigned_at=assigned_at,
            assigned_out_of_hours=out_of_hours,
            eligibility_check__category=self.category,
        )
        return case

    def get_new_value(self, case):
        return Case.objects.filter(pk=case.pk).values_list("assigned_out_of_hours", flat=True)[0]

    def call_command_and_expect_output(self, messages, commit=False):
        out = StringIO()
        command_args = ["recalculate_assigned_out_of_hours", self.dt]
        if commit:
            command_args.append("commit")
        call_command(*command_args, stdout=out)
        output = out.getvalue()
        for msg in messages:
            self.assertIn(msg, output)

    def test_incorrect_first_hour_of_business_bst(self):
        case = self.create(2021, 5, 5, 9, 30, True)
        self.call_command_and_expect_output(
            ["1 cases assigned since", "Not making changes", "1 cases will be changed to `False`"]
        )
        self.assertTrue(self.get_new_value(case))

        self.call_command_and_expect_output(
            ["Making changes", "1 cases will be changed to `False`", "1 cases changed to `False`"], commit=True
        )
        self.assertFalse(self.get_new_value(case))

    def test_correct_first_hour_of_business_bst(self):
        case = self.create(2021, 5, 5, 9, 30, False)
        self.call_command_and_expect_output(
            ["1 cases assigned since", "Not making changes", "1 cases already had the correct value"]
        )
        self.assertFalse(self.get_new_value(case))

        self.call_command_and_expect_output(
            ["Making changes", "0 cases changed to `True`", "0 cases changed to `False`"], commit=True
        )
        self.assertFalse(self.get_new_value(case))

    def test_correct_before_business_hours_bst(self):
        case = self.create(2021, 5, 5, 8, 30, True)
        self.call_command_and_expect_output(
            ["1 cases assigned since", "Not making changes", "1 cases already had the correct value"]
        )
        self.assertTrue(self.get_new_value(case))

        self.call_command_and_expect_output(
            ["Making changes", "0 cases changed to `True`", "0 cases changed to `False`"], commit=True
        )
        self.assertTrue(self.get_new_value(case))

    def test_correct_before_business_hours_gmt(self):
        case = self.create(2021, 2, 2, 8, 30, True)
        self.call_command_and_expect_output(
            ["1 cases assigned since", "Not making changes", "1 cases already had the correct value"]
        )
        self.assertTrue(self.get_new_value(case))

        self.call_command_and_expect_output(
            ["Making changes", "1 cases already had the correct value", "0 cases changed to `False`"], commit=True
        )
        self.assertTrue(self.get_new_value(case))

    def test_case_before_cutoff(self):
        case = self.create(2018, 5, 5, 8, 30, True)
        self.call_command_and_expect_output(["0 cases assigned since"])
        self.assertTrue(self.get_new_value(case))

    def test_multiple_cases(self):
        old_incorrect_bst = self.create(2018, 5, 9, 9, 30, True)
        correct_gmt = self.create(2021, 2, 2, 9, 30, False)
        incorrect_bst = self.create(2021, 5, 5, 9, 30, True)
        incorrect_bst_2 = self.create(2021, 5, 12, 9, 30, True)
        incorrect_bst_evening = self.create(2021, 5, 12, 17, 30, False)
        correct_bst = self.create(2021, 5, 19, 9, 30, False)
        self.call_command_and_expect_output(
            [
                "5 cases assigned since",
                "Not making changes",
                "2 cases already had the correct value",
                "2 cases will be changed to `False`",
                "1 cases will be changed to `True`",
            ]
        )

        self.call_command_and_expect_output(
            [
                "Making changes",
                "2 cases already had the correct value",
                "2 cases changed to `False`",
                "1 cases changed to `True`",
            ],
            commit=True,
        )
        self.assertTrue(self.get_new_value(old_incorrect_bst))
        self.assertFalse(self.get_new_value(correct_gmt))
        self.assertFalse(self.get_new_value(incorrect_bst))
        self.assertFalse(self.get_new_value(incorrect_bst_2))
        self.assertTrue(self.get_new_value(incorrect_bst_evening))
        self.assertFalse(self.get_new_value(correct_bst))
