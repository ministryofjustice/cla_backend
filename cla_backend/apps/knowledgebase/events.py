from cla_eventlog import event_registry
from cla_eventlog.constants import LOG_TYPES, LOG_LEVELS, LOG_ROLES
from cla_eventlog.events import BaseEvent, None_if_owned_by_op_or_op_manager


class AlternativeHelpEvent(BaseEvent):
    key = 'alternative_help'
    codes = {
        'IRKB': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [LOG_ROLES.OPERATOR, LOG_ROLES.SPECIALIST],
            'description': 'Assigned to alternative help from Knowledgebase',
            'stops_timer': True,
            'set_requires_action_by': None_if_owned_by_op_or_op_manager
        },
        'COSPF': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [LOG_ROLES.OPERATOR, LOG_ROLES.SPECIALIST],
            'description': 'Assigned to F2F provider',
            'stops_timer': True,
            'set_requires_action_by': None_if_owned_by_op_or_op_manager
        },
        'SPFN': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [LOG_ROLES.OPERATOR, LOG_ROLES.SPECIALIST],
            'description': 'Assigned to F2F provider (Housing and Family)',
            'stops_timer': True,
            'set_requires_action_by': None_if_owned_by_op_or_op_manager
        },
        'SPFM': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [LOG_ROLES.OPERATOR, LOG_ROLES.SPECIALIST],
            'description': 'Assigned to F2F provider (Debt, Education and Discrimination)',
            'stops_timer': True,
            'set_requires_action_by': None_if_owned_by_op_or_op_manager
        }
    }
event_registry.register(AlternativeHelpEvent)
