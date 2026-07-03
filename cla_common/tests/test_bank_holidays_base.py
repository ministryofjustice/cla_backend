from datetime import datetime
import unittest

from .. import call_centre_availability


class MonkeyPatch(object):
    def __init__(self, obj, attr, value):
        self.obj = obj
        self.attr = attr
        self.applied = False

        if hasattr(obj, attr):
            self.original = getattr(obj, attr)
            setattr(obj, attr, value)
            self.applied = True

    def undo(self):
        if self.applied:
            setattr(self.obj, self.attr, self.original)


def mock_bank_holidays():
    return [datetime(2014, 12, 25, 0, 0)]


class TestBankHolidaysBaseTestCase(unittest.TestCase):
    def setUp(self):
        self.bank_holiday_patch = MonkeyPatch(call_centre_availability, "bank_holidays", mock_bank_holidays)

    def tearDown(self):
        self.bank_holiday_patch.undo()
