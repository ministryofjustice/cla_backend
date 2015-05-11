import unittest

from celery import Celery
from django.conf import settings
from django.db import connection


class SmokeTests(unittest.TestCase):

    def setUp(self):
        pass

    def test_can_access_db(self):
        "access the database"
        cursor = connection.cursor()
        cursor.execute('SELECT 1')
        row = cursor.fetchone()
        self.assertEqual(1, row[0])

    def test_can_access_celery(self):
        "connect to SQS"
        if not getattr(settings, 'CELERY_ALWAYS_EAGER', False):
            app = Celery('cla_backend')
            app.config_from_object('django.conf:settings')
            conn = app.connection()i
            conn.connect()
            conn.release()
