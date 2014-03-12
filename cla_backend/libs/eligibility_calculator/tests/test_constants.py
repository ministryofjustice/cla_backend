import unittest

from ..constants import disposable_capital
from ..constants import gross_income


class DisposableCapitalTestCase(unittest.TestCase):
    def test_get_limit_immigration(self):
        self.assertEqual(
            disposable_capital.get_limit('immigration'),
            disposable_capital.LIMIT_IMMIGRATION
        )

    def test_get_limit_debt(self):
        self.assertEqual(
            disposable_capital.get_limit('debt'),
            disposable_capital.LIMIT_DEFAULT
        )


class GrossIncomeTestCase(unittest.TestCase):
    def test_get_limit_no_dependants(self):
        """
        No dependants => no extra relief
        """
        self.assertEqual(
            gross_income.get_limit(),
            gross_income.BASE_LIMIT
        )

    def test_get_limit_4_dependants(self):
        """
        No extra relief for the first 4 dependants
        """
        self.assertEqual(
            gross_income.get_limit(dependant_children=4),
            gross_income.BASE_LIMIT
        )

    def test_get_limit_5_dependants(self):
        """
        gross_income.EXTRA_CHILD_MODIFIER relief for each dependants after the
        4th one.

        So in this case the relief is (gross_income.EXTRA_CHILD_MODIFIER * 1)
        """
        self.assertEqual(
            gross_income.get_limit(dependant_children=5),
            gross_income.BASE_LIMIT + gross_income.EXTRA_CHILD_MODIFIER
        )

    def test_get_limit_6_dependants(self):
        """
        gross_income.EXTRA_CHILD_MODIFIER relief for each dependants after the
        4th one.

        So in this case the relief is (gross_income.EXTRA_CHILD_MODIFIER * 2)
        """
        self.assertEqual(
            gross_income.get_limit(dependant_children=6),
            gross_income.BASE_LIMIT + (gross_income.EXTRA_CHILD_MODIFIER*2)
        )
