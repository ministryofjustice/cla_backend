import datetime
from unittest import TestCase
import mock
import jsonpatch
from core.utils import format_patch
from cla_common.call_centre_availability import OpeningHours
from legalaid.utils import sla


class FormatPatchTestCase(TestCase):
    def setUp(self):
        self.initial = {"foo": 1, "bar": "bar", "list": ["baz", "baz"]}

    def test_format_simple_change(self):

        b = self.initial.copy()
        b["foo"] = 2
        # b['bar'] = 'rab'
        # b['list'] = reversed(b['list'])

        patch = jsonpatch.JsonPatch.from_diff(self.initial, b)
        formatted = format_patch(patch)
        self.assertIsInstance(formatted, basestring)
        self.assertEqual(formatted, "Changed foo to 2")


class CallCentreFixedOperatingHours(object):
    def setUp(self):
        super(CallCentreFixedOperatingHours, self).setUp()

        hours = {
            "weekday": (datetime.time(9, 0), datetime.time(20, 0)),
            "saturday": (datetime.time(9, 0), datetime.time(12, 30)),
        }
        operator_hours = OpeningHours(**hours)

        self.operator_hours_patcher = mock.patch.object(sla, "operator_hours", operator_hours)
        self.operator_hours_patcher.start()

    def tearDown(self):
        self.operator_hours_patcher.stop()
