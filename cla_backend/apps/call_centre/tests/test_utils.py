from unittest import TestCase
import jsonpatch
from ..utils import format_patch

class FormatPatchTestCase(TestCase):

    def setUp(self):
        self.initial = {
            'foo': 1,
            'bar': 'bar',
            'list': ['baz', 'baz']
        }

    def test_format_simple_change(self):

        b = self.initial.copy()
        b['foo'] = 2
        # b['bar'] = 'rab'
        # b['list'] = reversed(b['list'])

        patch = jsonpatch.JsonPatch.from_diff(self.initial, b)
        formatted = format_patch(patch)
        self.assertIsInstance(formatted, basestring)
        self.assertEqual(formatted, 'Changed foo to 2')