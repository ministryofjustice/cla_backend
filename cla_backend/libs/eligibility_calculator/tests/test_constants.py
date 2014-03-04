import unittest

from ..constants import disposable_capital


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
