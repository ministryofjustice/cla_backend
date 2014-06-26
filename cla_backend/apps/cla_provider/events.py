from cla_eventlog import event_registry
from cla_eventlog.constants import LOG_TYPES, LOG_LEVELS, LOG_ROLES
from cla_eventlog.events import BaseEvent


class RejectCaseEvent(BaseEvent):
    key = 'reject_case'
    codes = {
        'MIS-MER': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [LOG_ROLES.SPECIALIST],
            'description': 'Misdiagnosed, case lacks sufficient merit'
        },
        'MIS-MEANS': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [LOG_ROLES.SPECIALIST],
            'description': 'Misdiagnosed, means test isn\'t correct'
        },
        'MIS-OOS': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [LOG_ROLES.SPECIALIST],
            'description': 'Misdiagnosed, out of scope'
        },
        'MIS-TEL': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [LOG_ROLES.SPECIALIST],
            'description': 'Misdiagnosed, case not suitable for telephone advice'
        }
    }
event_registry.register(RejectCaseEvent)

class AcceptCaseEvent(BaseEvent):
    key = 'accept_case'
    codes = {
        'SPOP': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [],
            'description': 'Case taken'
        },
    }
event_registry.register(AcceptCaseEvent)

class CloseCaseEvent(BaseEvent):
    key = 'close_case'
    codes = {
        'CLSP': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [],
            'description': 'Closed SP Case'
        }
    }
event_registry.register(CloseCaseEvent)
