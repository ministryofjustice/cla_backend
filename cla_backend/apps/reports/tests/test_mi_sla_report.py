# -*- coding: utf-8 -*-
from contextlib import contextmanager
import datetime
from django.test import TestCase
from legalaid.forms import get_sla_time
import mock

from core.tests.mommy_utils import make_recipe, make_user
from cla_eventlog import event_registry
from cla_eventlog.models import Log
from reports.forms import MICB1Extract


@contextmanager
def patch_field(cls, field_name, dt):
    field = cls._meta.get_field(field_name)
    mock_now = lambda: dt
    with mock.patch.object(field, 'default', new=mock_now):
        yield


class MiSlaTestCase(TestCase):
    def test_call_started_sla(self):
        with patch_field(Log, 'created', datetime.datetime(2015, 1, 2, 9, 0, 0)):
            case = make_recipe('legalaid.case')

        user = make_user()
        make_recipe('call_centre.operator', user=user)

        event = event_registry.get_event('call_me_back')()
        _dt = datetime.datetime(2015, 1, 2, 9, 1, 0)
        with patch_field(Log, 'created', datetime.datetime(2015, 1, 2, 9, 1, 0)):
            event.get_log_code(case=case)
            event.process(
                case, created_by=user,
                notes='',
                context={
                    'requires_action_at': _dt,
                    'sla_15': get_sla_time(_dt, 15),
                    'sla_30': get_sla_time(_dt, 30),
                    'sla_120': get_sla_time(_dt, 120),
                    'sla_480': get_sla_time(_dt, 480)
                },
            )

        case.requires_action_at = _dt
        case.save()

        event = event_registry.get_event('case')()
        with patch_field(Log, 'created', datetime.datetime(2015, 1, 2, 9, 30, 0)):
            event.process(
                case, status='call_started', created_by=user,
                notes='Call started'
            )

        date_range = (
            datetime.datetime(2015, 1, 1),
            datetime.datetime(2015, 2, 1)
        )

        with mock.patch('reports.forms.MICB1Extract.date_range', date_range):
            report = MICB1Extract()

            qs = report.get_queryset()

        self.assertFalse(qs[0][28])
