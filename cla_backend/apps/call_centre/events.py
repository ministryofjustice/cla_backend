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
        is_spor = kwargs.get('is_spor', False)

        if is_spor:
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


class CallMeBackEvent(BaseEvent):
    key = 'call_me_back'
    codes = {
        'CB1': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [LOG_ROLES.OPERATOR],
            'description': 'Callback 1',
            'stops_timer': True,
            'set_requires_action_by': REQUIRES_ACTION_BY.OPERATOR
        },
        'CB2': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [LOG_ROLES.OPERATOR],
            'description': 'Callback 2',
            'stops_timer': True,
            'set_requires_action_by': REQUIRES_ACTION_BY.OPERATOR
        },
        'CB3': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [LOG_ROLES.OPERATOR],
            'description': 'Callback 3',
            'stops_timer': True,
            'set_requires_action_by': REQUIRES_ACTION_BY.OPERATOR
        }
    }

    def get_log_code(self, case=None, **kwargs):
        if not case:
            raise ValueError('a case obj should be passed in')

        if case.callback_attempt == 0:
            return 'CB1'
        if case.callback_attempt == 1:
            return 'CB2'
        if case.callback_attempt == 2:
            return 'CB3'

        raise ValueError('Reached max number of callbacks allowed')

event_registry.register(CallMeBackEvent)


class StopCallMeBackEvent(BaseEvent):
    key = 'stop_call_me_back'
    codes = {
        'CBC': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [LOG_ROLES.OPERATOR],
            'description': 'Callback Cancelled',
            'stops_timer': True,
            'set_requires_action_by': None_if_owned_by_operator
        },
        'CALLBACK_COMPLETE': {
            'type': LOG_TYPES.SYSTEM,
            'level': LOG_LEVELS.MINOR,
            'selectable_by': [],
            'description': 'Callback complete',
            'stops_timer': False
        }
    }

    def get_log_code(self, case=None, **kwargs):
        if not case:
            raise ValueError('A case obj should be passed in')
        cancel = kwargs.get('cancel', False)
        complete = kwargs.get('complete', False)

        if not cancel and not complete:
            raise ValueError('cancel or complete should be passed in')

        if cancel:
            if case.callback_attempt == 0:
                raise ValueError('Cannot cancel callback without a previous CBx')
            return 'CBC'

        if complete:
            if case.callback_attempt == 0:
                raise ValueError('Cannot mark callback as complete without previous CBx')
            return 'CALLBACK_COMPLETE'

event_registry.register(StopCallMeBackEvent)
