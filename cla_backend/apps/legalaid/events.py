from cla_eventlog import event_registry
from cla_eventlog.constants import LOG_TYPES, LOG_LEVELS
from cla_eventlog.events import BaseEvent

class MeansTestEvent(BaseEvent):
    key = 'means_test'
    codes = {
        'MT_CREATED': {
            'type': LOG_TYPES.SYSTEM,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [],
            'description': "Means test created"
        },
        'MT_CHANGED': {
            'type': LOG_TYPES.SYSTEM,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [],
            'description': "Means test changed"
        },
        'MT_PASSED': {
            'type': LOG_TYPES.SYSTEM,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [],
            'description': "Means test passed"
        }
        ,
        'MT_FAILED': {
            'type': LOG_TYPES.SYSTEM,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [],
            'description': "Means test failed"
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

