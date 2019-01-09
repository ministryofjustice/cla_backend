# -*- coding: utf-8 -*-
import datetime
from django.utils.unittest import TestCase

from ..serializers import PPSerializer


class SerializerTestCase(TestCase):
    def test_from_to_time_is_monday_a_week_ago_and_last_monday(self):
        serializer = PPSerializer(datetime.datetime(2015, 7, 13, 1, 56, 43, 398))

        self.assertEqual(serializer.from_time, datetime.datetime(2015, 7, 6, 0, 0, 0))
        self.assertEqual(serializer.to_time, datetime.datetime(2015, 7, 13, 0, 0, 0))
        self.assertEqual(serializer.time_string, "2015-07-06T00:00:00+00:00")
