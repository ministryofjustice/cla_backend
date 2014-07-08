from cla_eventlog import event_registry
from cla_eventlog.constants import LOG_TYPES, LOG_LEVELS
from cla_eventlog.events import BaseEvent

from cla_eventlog.models import Log


class MeansTestEvent(BaseEvent):
    key = 'means_test'
    codes = {
        'MT_CREATED': {
            'type': LOG_TYPES.SYSTEM,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [],
            'description': "Means test created",
            'stops_timer': False
        },
        'MT_CHANGED': {
            'type': LOG_TYPES.SYSTEM,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [],
            'description': "Means test changed",
            'stops_timer': False
        },
        'MT_PASSED': {
            'type': LOG_TYPES.SYSTEM,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [],
            'description': "Means test passed",
            'stops_timer': False
        },
        'MT_FAILED': {
            'type': LOG_TYPES.SYSTEM,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [],
            'description': "Means test failed",
            'stops_timer': False
        },
        }

    def get_log_code(self, **kwargs):
        status = kwargs['status']
        lookup = {
            'created': 'MT_CREATED',
            'changed': 'MT_CHANGED',
            'passed':  'MT_PASSED',
            'failed':  'MT_FAILED',
            }

        return lookup[status]
event_registry.register(MeansTestEvent)


class CaseEvent(BaseEvent):
    key = 'case'
    codes = {
        'CASE_CREATED': {
            'type': LOG_TYPES.SYSTEM,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [],
            'description': "Case created",
            'stops_timer': False
        },
        'CASE_VIEWED': {
            'type': LOG_TYPES.SYSTEM,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [],
            'description': "Case viewed",
            'stops_timer': False
        },
    }

    def save_log(self, log):
        to_be_saved = True

        if log.code == 'CASE_VIEWED':
            # checking that doesn't exist 'created' or 'viewed' log entry
            # for this timer in the db already do that I don't duplicate
            # events.
            # TODO: might be slow, is there a better way?
            to_be_saved = Log.objects.filter(
                timer=log.timer, case=log.case, 
                code__in=['CASE_CREATED', 'CASE_VIEWED']
            ).count() == 0

        if to_be_saved:
            log.save(force_insert=True)

    def get_log_code(self, **kwargs):
        status = kwargs['status']
        lookup = {
            'created': 'CASE_CREATED',
            'viewed': 'CASE_VIEWED',
        }

        return lookup[status]
event_registry.register(CaseEvent)
