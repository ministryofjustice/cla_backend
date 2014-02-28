import unittest
from ..calculator import EligibilityChecker
from ..models import CaseData
from ..exceptions import PropertyExpectedException

class TestCaseData(unittest.TestCase):

    GROSS_INCOME_FIELDS = [
        'earnings',
        'other_income',
    ]

    def setUp(self):
        self.default_case_data_dict = \
        {'category': u'blah blah',
         'criminal_legalaid_contributions': 0,
         'dependant_children': 0,
         'earnings': 11,
         'has_partner': False,
         'income_tax_and_ni': 0,
         'investments': 22,
         'is_partner_opponent': False,
         'is_you_or_your_partner_over_60': False,
         'maintenance': 0,
         'money_owed': 22,
         'mortgage_or_rent': 0,
         'on_passported_benefits': False,
         'other_income': 22,
         'property_data': [(22, 0, 100)],
         'savings': 22,
         'self_employed': False,
         'valuable_items': 22}

    def test_total_income_calculation(self):
        cd = CaseData(**self.default_case_data_dict)
        ti = cd.total_income()
        gross_income_orig = sum(self.default_case_data_dict.get(f, 0) for f in self.GROSS_INCOME_FIELDS)
        self.assertEqual(gross_income_orig, ti)

    def test_bad_property_set_exception(self):
        cdd = self.default_case_data_dict
        cdd['foo'] = 'bar'
        with self.assertRaises(PropertyExpectedException):
            cd = CaseData(**cdd)
