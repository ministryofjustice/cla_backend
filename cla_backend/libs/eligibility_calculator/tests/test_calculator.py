import unittest

from ..calculator import EligibilityChecker
from ..models import CaseData
from ..exceptions import PropertyExpectedException
from .. import constants

from . import fixtures


class TestCalculator(unittest.TestCase):

    def get_default_case_data(self, **kwargs):
        """
        gives default case_data with each kwarg
        overridden

        :param kwargs: things to overwrite in the default case_data
        :return: CaseData object with default values
        """
        return CaseData(**fixtures.get_default_case_data(**kwargs))

    def setUp(self):
        self.default_calculator = EligibilityChecker(self.get_default_case_data())

    def test_gross_income_is_eligible(self):
        too_little_money = constants.gross_income.BASE_LIMIT - 1
        case_data = self.get_default_case_data(you__income__earnings=too_little_money)
        is_elig = EligibilityChecker(case_data).is_gross_income_eligible()
        self.assertTrue(is_elig)

    def test_gross_income_is_ineligible(self):
        too_much_money = constants.gross_income.BASE_LIMIT + 1
        case_data = self.get_default_case_data(you__income__earnings=too_much_money)
        is_elig = EligibilityChecker(case_data).is_gross_income_eligible()
        self.assertFalse(is_elig)

    def test_base_limit_gross_income_is_ineligible(self):
        """
        TEST: gross_income limit doesn't rise for 1-4 children.
        Should reject someone for having income more than 2657
        """
        too_much_money = constants.gross_income.BASE_LIMIT + 1
        for dep_children in range(1,constants.gross_income.INCLUSIVE_CHILDREN_BASE+1):
            case_data = self.get_default_case_data(
                you__income__earnings=too_much_money,
                facts__dependant_children=dep_children
            )
            is_elig = EligibilityChecker(case_data).is_gross_income_eligible()
            self.assertFalse(is_elig)

    def test_base_limit_gross_income_is_eligible(self):
        """
        if you have > 4 children then earning 1 more than base limit
        should be fine.
        """
        too_much_money = constants.gross_income.BASE_LIMIT + 1
        case_data = self.get_default_case_data(
            you__income__earnings=too_much_money,
            facts__dependant_children=5
        )
        is_elig = EligibilityChecker(case_data).is_gross_income_eligible()
        self.assertTrue(is_elig)
