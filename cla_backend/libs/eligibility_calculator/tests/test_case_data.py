import unittest
from ..models import CaseData
from ..exceptions import PropertyExpectedException
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
        cdd = get_default_case_data(foo='bar')
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
            savings=0,
            money_owed=0,
            valuable_items=0,
            investments=0,
            partner_savings=0,
            partner_money_owed=0,
            partner_valuable_items=0,
            partner_investments=0
        )
        cd = CaseData(**cdd)
        self.assertEqual(0, cd.get_liquid_capital())
