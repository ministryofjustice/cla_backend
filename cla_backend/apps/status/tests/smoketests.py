import unittest

from celery import Celery
from django.conf import settings
from django.db import connection


class SmokeTests(unittest.TestCase):

    def setUp(self):
        pass

    def test_can_access_db(self):
        cursor = connection.cursor()
        cursor.execute('SELECT 1')
        row = cursor.fetchone()
        self.assertEqual(1, row[0])

    def test_can_access_celery(self):
        if not getattr(settings, 'CELERY_ALWAYS_EAGER', False):
            conn = Celery('cla_backend').connection()
            conn.connect()
            conn.release()
