import unittest

from .. import constants


class DisposableCapitalTestCase(unittest.TestCase):
    def test_get_limit_immigration(self):
        self.assertEqual(constants.get_disposable_capital_limit("immigration"), constants.LIMIT_IMMIGRATION)

    def test_get_limit_debt(self):
        self.assertEqual(constants.get_disposable_capital_limit("debt"), constants.LIMIT_DEFAULT)


class GrossIncomeTestCase(unittest.TestCase):
    def test_get_limit_no_dependants(self):
        """
        No dependants => no extra relief
        """
        self.assertEqual(constants.get_gross_income_limit(), constants.BASE_LIMIT)

    def test_get_limit_4_dependants(self):
        """
        No extra relief for the first 4 dependants
        """
        self.assertEqual(constants.get_gross_income_limit(dependant_children=4), constants.BASE_LIMIT)

    def test_get_limit_5_dependants(self):
        """
        gross_income.EXTRA_CHILD_MODIFIER relief for each dependants after the
        4th one.

        So in this case the relief is (gross_income.EXTRA_CHILD_MODIFIER * 1)
        """
        self.assertEqual(
            constants.get_gross_income_limit(dependant_children=5),
            constants.BASE_LIMIT + constants.EXTRA_CHILD_MODIFIER,
        )

    def test_get_limit_6_dependants(self):
        """
        gross_income.EXTRA_CHILD_MODIFIER relief for each dependants after the
        4th one.

        So in this case the relief is (gross_income.EXTRA_CHILD_MODIFIER * 2)
        """
        self.assertEqual(
            constants.get_gross_income_limit(dependant_children=6),
            constants.BASE_LIMIT + (constants.EXTRA_CHILD_MODIFIER * 2),
        )
