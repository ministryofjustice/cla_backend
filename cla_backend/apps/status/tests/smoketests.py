import unittest

from django.db import connection


class SmokeTests(unittest.TestCase):

    def setUp(self):
        pass

    def test_can_access_db(self):
        cursor = connection.cursor()
        cursor.execute('SELECT 1')
        row = cursor.fetchone()
        self.assertEqual(1, row[0])
