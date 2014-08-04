from cla_common.constants import ELIGIBILITY_STATES, REQUIRES_ACTION_BY

from cla_eventlog import event_registry
from cla_eventlog.constants import LOG_TYPES, LOG_LEVELS, LOG_ROLES
from cla_eventlog.events import BaseEvent, None_if_owned_by_operator


class AssignToProviderEvent(BaseEvent):
    key = 'assign_to_provider'
    codes = {
        'REFSP': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [],
            'description': 'Referred to Specialist',
            'stops_timer': True,
            'set_requires_action_by': REQUIRES_ACTION_BY.PROVIDER_REVIEW
        },
        'MANALC': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [],
            'description': 'Manually allocated to Specialist',
            'stops_timer': True,
            'set_requires_action_by': REQUIRES_ACTION_BY.PROVIDER_REVIEW
        },
        'SPOR': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [],
            'description': 'Referred to Specialist for second opinion',
            'stops_timer': True,
            'set_requires_action_by': REQUIRES_ACTION_BY.PROVIDER_REVIEW
        },
    }

    def get_log_code(self, case=None, **kwargs):

        if case:
            is_eligible = case.eligibility_check and \
                case.eligibility_check.state == ELIGIBILITY_STATES.YES

            if not is_eligible or not case.in_scope:
                return 'SPOR'

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
            'stops_timer': True,
            'set_requires_action_by': None_if_owned_by_operator
        },
        'DECL': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [LOG_ROLES.OPERATOR],
            'description': 'Client declined all help options',
            'stops_timer': True,
            'set_requires_action_by': None_if_owned_by_operator
        },
        'NRES': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [LOG_ROLES.OPERATOR],
            'description': 'No resources available to help',
            'stops_timer': True,
            'set_requires_action_by': None_if_owned_by_operator
        },
    }
event_registry.register(DeclineHelpEvent)

