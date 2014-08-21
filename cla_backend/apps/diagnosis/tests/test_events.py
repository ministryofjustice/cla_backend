from django.test import TestCase

from cla_eventlog.tests.base import EventTestCaseMixin
from cla_eventlog.constants import LOG_TYPES


class DiagnosisEventTestCase(EventTestCaseMixin, TestCase):
    EVENT_KEY = 'diagnosis'

    def test_diagnosis_created(self):
        self._test_process_with_implicit_code(
            'DIAGNOSIS_CREATED',
            process_kwargs={
                'status': 'created'
            },
            expected_type=LOG_TYPES.SYSTEM
        )

    def test_diagnosis_deleted(self):
        self._test_process_with_implicit_code(
            'DIAGNOSIS_DELETED',
            process_kwargs={
                'status': 'deleted'
            },
            expected_type=LOG_TYPES.SYSTEM
        )
