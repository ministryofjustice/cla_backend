from cla_eventlog import event_registry
from cla_eventlog.constants import LOG_TYPES, LOG_LEVELS, LOG_ROLES
from cla_eventlog.events import BaseEvent


class AssignToProviderEvent(BaseEvent):
    key = 'assign_to_provider'
    codes = {
        'REFSP': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [],
            'description': 'Referred to Specialist',
            'stops_timer': True
        },
        'MANALC': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [],
            'description': 'Manually allocated to Specialist',
            'stops_timer': True
        },
        'RDSP': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [LOG_ROLES.OPERATOR],
            'description': 'Sent to Specialist again',
            'stops_timer': True
        },
    }

    def get_log_code(self, **kwargs):
        is_manual = kwargs['is_manual']

        if is_manual:
            return 'MANALC'

        return 'REFSP'

event_registry.register(AssignToProviderEvent)


class DeferAssignmentEvent(BaseEvent):
    key = 'defer_assignment'
    codes = {
        'CBSP': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [LOG_ROLES.OPERATOR],
            'description': 'Will call back later for Specialist',
            'stops_timer': True
        }
    }
event_registry.register(DeferAssignmentEvent)


class DeclineHelpEvent(BaseEvent):
    key = 'decline_help'
    codes = {
        'DESP': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [LOG_ROLES.OPERATOR],
            'description': 'Client declined Specialist',
            'stops_timer': True
        },
        'DECL': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [LOG_ROLES.OPERATOR],
            'description': 'Client declined all help options',
            'stops_timer': True
        },
        'NRES': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [LOG_ROLES.OPERATOR],
            'description': 'No resources available to help',
            'stops_timer': True
        },
    }
event_registry.register(DeclineHelpEvent)
