import random
import unittest

from ..models import CaseData
from ..exceptions import PropertyExpectedException, InvalidStateException
from .fixtures import get_default_case_data


class TestCaseData(unittest.TestCase):

    GROSS_INCOME_FIELDS = [
        'earnings',
        'other_income',
    ]

    GROSS_CAPITAL_FIELDS = [
        'savings',
        'investments',
        'money_owed',
        'valuable_items',
        'partner_savings',
        'partner_investments',
        'partner_money_owed',
        'partner_valuable_items'
    ]


    def test_total_income_calculation(self):
        default_data = get_default_case_data()
        cd = CaseData(**default_data)
        ti = cd.total_income()
        gross_income_orig = sum(default_data.get(f, 0) for f in self.GROSS_INCOME_FIELDS)
        self.assertEqual(gross_income_orig, ti)

    def test_bad_property_set_exception(self):
        cdd = get_default_case_data(foo='bar', bar__baz=24)
        with self.assertRaises(PropertyExpectedException):
            cd = CaseData(**cdd)

    def test_getattr_raises_if_accessing_invalid_prop(self):
        with self.assertRaises(AttributeError):
            cd = CaseData()
            cd.foo

    def test_get_total_income_no_partner(self):
        cdd = get_default_case_data(
            earnings=265700,
            other_income=0
        )
        cd = CaseData(**cdd)
        self.assertEqual(265700, cd.total_income())

    def test_get_total_income_incl_other_no_partner(self):
        cdd = get_default_case_data(
            earnings=265700,
            other_income=100
        )
        cd = CaseData(**cdd)
        self.assertEqual(265800, cd.total_income())

    def test_provide_partner_earnings_required_partner_other_income(self):
        with self.assertRaises(PropertyExpectedException):
            cdd = get_default_case_data(
                earnings=1,
                other_income=1,
                partner_earnings=1,
                has_partner=True
            )
            cd = CaseData(**cdd)
            cd.total_income()

    def test_get_total_income_with_partner(self):
        cdd = get_default_case_data(
            earnings=265700,
            other_income=0,
            partner_earnings=100,
            partner_other_income=0,
            has_partner=True
        )
        cd = CaseData(**cdd)
        self.assertEqual(265800, cd.total_income())

    def test_get_total_income_incl_other_with_partner(self):
        cdd = get_default_case_data(
            earnings=265700,
            other_income=100,
            partner_earnings=100,
            partner_other_income=0,
            has_partner=True
        )
        cd = CaseData(**cdd)
        self.assertEqual(265900, cd.total_income())

    def test_is_partner_disputed_true(self):
        cdd = get_default_case_data(has_partner=True, is_partner_opponent=True)
        cd = CaseData(**cdd)
        self.assertTrue(cd.has_disputed_partner())

    def test_is_partner_disputed_false(self):
        cdd = get_default_case_data(has_partner=False, is_partner_opponent=True)
        cd = CaseData(**cdd)
        self.assertFalse(cd.has_disputed_partner())

    def test_is_partner_disputed_not_opponent(self):
        cdd = get_default_case_data(has_partner=True, is_partner_opponent=False)
        cd = CaseData(**cdd)
        self.assertFalse(cd.has_disputed_partner())

    def test_is_partner_disputed_no_partner_not_opponent(self):
        cdd = get_default_case_data(has_partner=False, is_partner_opponent=False)
        cd = CaseData(**cdd)
        self.assertFalse(cd.has_disputed_partner())

    def test_get_liquid_capital(self):
        cdd = get_default_case_data(
            you__savings__savings=0,
            you__savings__money_owed=0,
            you__savings__valuable_items=0,
            you__savings__investments=0,
            partner__savings__savings=0,
            partner__savings__money_owed=0,
            partner__savings__valuable_items=0,
            partner__savings__investments=0
        )
        cd = CaseData(**cdd)
        self.assertEqual(0, cd.get_liquid_capital())

    def test_get_liquid_capital_savings_only(self):
        cdd = get_default_case_data(
            savings=10000,
            money_owed=0,
            valuable_items=0,
            investments=0,
            partner_savings=0,
            partner_money_owed=0,
            partner_valuable_items=0,
            partner_investments=0
        )
        cd = CaseData(**cdd)
        self.assertEqual(10000, cd.get_liquid_capital())

    def test_get_liquid_capital_savings_money_owed(self):
        cdd = get_default_case_data(
            savings=10000,
            money_owed=10,
            valuable_items=0,
            investments=0,
            partner_savings=0,
            partner_money_owed=0,
            partner_valuable_items=0,
            partner_investments=0
        )
        cd = CaseData(**cdd)
        self.assertEqual(10010, cd.get_liquid_capital())

    def test_get_liquid_capital_savings_valuable(self):
        cdd = get_default_case_data(
            savings=10000,
            money_owed=0,
            valuable_items=1000,
            investments=0,
            partner_savings=0,
            partner_money_owed=0,
            partner_valuable_items=0,
            partner_investments=0
        )
        cd = CaseData(**cdd)
        self.assertEqual(11000, cd.get_liquid_capital())

    def test_get_liquid_capital_savings_investments(self):
        cdd = get_default_case_data(
            savings=10000,
            money_owed=0,
            valuable_items=0,
            investments=5000,
            partner_savings=0,
            partner_money_owed=0,
            partner_valuable_items=0,
            partner_investments=0
        )
        cd = CaseData(**cdd)
        self.assertEqual(15000, cd.get_liquid_capital())

    def test_inconsistent_state(self):
        cdd = get_default_case_data(
            savings=10000,
            money_owed=0,
            valuable_items=0,
            investments=0,
            partner_savings=10000,
            partner_money_owed=0,
            partner_valuable_items=0,
            partner_investments=0,
            has_partner=False,
        )
        with self.assertRaises(InvalidStateException):
            cd = CaseData(**cdd)

    def test_get_liquid_capital_savings_with_partner(self):
        cdd = get_default_case_data(
            savings=10000,
            money_owed=0,
            valuable_items=0,
            investments=0,
            partner_savings=1,
            partner_money_owed=0,
            partner_valuable_items=0,
            partner_investments=0,
            has_partner=True
        )
        cd = CaseData(**cdd)
        self.assertEqual(10001, cd.get_liquid_capital())

    def test_get_liquid_capital_savings_with_partner_money_owed(self):
        cdd = get_default_case_data(
            savings=10000,
            money_owed=00,
            valuable_items=0,
            investments=0,
            partner_savings=0,
            partner_money_owed=20,
            partner_valuable_items=0,
            partner_investments=0,
            has_partner=True
        )
        cd = CaseData(**cdd)
        self.assertEqual(10020, cd.get_liquid_capital())

    def test_get_liquid_capital_savings_with_partner_savings(self):
        cdd = get_default_case_data(
            savings=10000,
            money_owed=00,
            valuable_items=0,
            investments=0,
            partner_savings=10,
            partner_money_owed=0,
            partner_valuable_items=0,
            partner_investments=0,
            has_partner=True
        )
        cd = CaseData(**cdd)
        self.assertEqual(10010, cd.get_liquid_capital())

    def test_get_liquid_capital_savings_with_partner_valuables(self):
        cdd = get_default_case_data(
            savings=10000,
            money_owed=00,
            valuable_items=5000,
            investments=0,
            partner_savings=0,
            partner_money_owed=0,
            partner_valuable_items=0,
            partner_investments=0,
            has_partner=True
        )
        cd = CaseData(**cdd)
        self.assertEqual(15000, cd.get_liquid_capital())

    def test_get_liquid_capital_savings_with_partner_investments(self):
        cdd = get_default_case_data(
            savings=10000,
            money_owed=00,
            valuable_items=0,
            investments=0,
            partner_savings=0,
            partner_money_owed=0,
            partner_valuable_items=0,
            partner_investments=100,
            has_partner=True
        )
        cd = CaseData(**cdd)
        self.assertEqual(10100, cd.get_liquid_capital())

    def test_get_liquid_capital_savings_only_partner_savings(self):
        cdd = get_default_case_data(
            savings=0,
            money_owed=0,
            valuable_items=0,
            investments=0,
            partner_savings=0,
            partner_money_owed=0,
            partner_valuable_items=0,
            partner_investments=100,
            has_partner=True
        )
        cd = CaseData(**cdd)
        self.assertEqual(100, cd.get_liquid_capital())

    def test_get_liquid_capital_savings_only_partner_money_owed(self):
        cdd = get_default_case_data(
            savings=0,
            money_owed=200,
            valuable_items=0,
            investments=0,
            partner_savings=0,
            partner_money_owed=0,
            partner_valuable_items=0,
            partner_investments=0,
            has_partner=True
        )
        cd = CaseData(**cdd)
        self.assertEqual(200, cd.get_liquid_capital())

    def test_get_liquid_capital_savings_random_values_no_partner(self):
        for i in range(0, 500):
            # ghetto quick-check
            steps = [random.randint(0, 50000)]
            for n in range(3):
                step = random.randint(0, steps[-1])
                steps.append(step)

            cdd = get_default_case_data(
                savings=steps[0],
                money_owed=steps[1],
                valuable_items=steps[2],
                investments=steps[3],
            )
            cd = CaseData(**cdd)
            self.assertEqual(sum(steps), cd.get_liquid_capital())

    def test_get_liquid_capital_savings_random_values_with_partner(self):
        for i in range(0, 500):
            # ghetto quick-check
            steps = [random.randint(0, 50000)]
            for n in range(7):
                step = random.randint(0, steps[-1])
                steps.append(step)

            cdd = get_default_case_data(
                savings=steps[0],
                money_owed=steps[1],
                valuable_items=steps[2],
                investments=steps[3],
                partner_savings=steps[4],
                partner_money_owed=steps[5],
                partner_valuable_items=steps[6],
                partner_investments=steps[7],
                has_partner=True
                )
            cd = CaseData(**cdd)
            self.assertEqual(sum(steps), cd.get_liquid_capital())

    def test_get_liquid_capital_savings_random_values_only_partner(self):
        for i in range(0, 500):
            # ghetto quick-check
            steps = [random.randint(0, 50000)]
            for n in range(3):
                step = random.randint(0, steps[-1])
                steps.append(step)

            cdd = get_default_case_data(
                savings=0,
                money_owed=0,
                valuable_items=0,
                investments=0,
                partner_savings=steps[0],
                partner_money_owed=steps[1],
                partner_valuable_items=steps[2],
                partner_investments=steps[3],
                has_partner=True
            )
            cd = CaseData(**cdd)
            self.assertEqual(sum(steps), cd.get_liquid_capital())


    def test_get_property_capital(self):
        cdd = get_default_case_data(

        )