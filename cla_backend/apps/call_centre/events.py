from cla_eventlog import event_registry
from cla_eventlog.constants import LOG_TYPES, LOG_LEVELS, LOG_ROLES
from cla_eventlog.events import BaseEvent


class DeferAssignmentEvent(BaseEvent):
    key = 'defer_assignment'
    codes = {
        'CBSP': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [LOG_ROLES.OPERATOR],
            'description': 'Will call back later for Specialist'
        }
    }
event_registry.register(DeferAssignmentEvent)
