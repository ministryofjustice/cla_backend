from cla_common.constants import REQUIRES_ACTION_BY

from cla_eventlog import event_registry
from cla_eventlog.constants import LOG_TYPES, LOG_LEVELS, LOG_ROLES
from cla_eventlog.events import BaseEvent, None_if_owned_by_operator
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
            'level': LOG_LEVELS.MINOR,
            'selectable_by': [],
            'description': "Case viewed",
            'stops_timer': False
        },
    }

    def save_log(self, log):
        to_be_saved = True

        if log.code == 'CASE_VIEWED' and log.timer:
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


class SuspendCaseEvent(BaseEvent):
    key = 'suspend_case'
    codes = {
        'INSUF': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.MODERATE,
            'selectable_by': [LOG_ROLES.OPERATOR],
            'description': 'Not enough info to continue',
            'stops_timer': True,
            'set_requires_action_by': None_if_owned_by_operator
        },
        'ABND': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.MODERATE,
            'selectable_by': [LOG_ROLES.OPERATOR, LOG_ROLES.SPECIALIST],
            'description': 'Client abandoned call',
            'stops_timer': True
        },
        'TERM': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.MODERATE,
            'selectable_by': [LOG_ROLES.OPERATOR, LOG_ROLES.SPECIALIST],
            'description': 'Hung up call',
            'stops_timer': True,
            'set_requires_action_by': None_if_owned_by_operator
        },
        'IRCB': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [LOG_ROLES.OPERATOR],
            'description': 'Booked appointment with senior member of staff',
            'stops_timer': True,
            'set_requires_action_by': REQUIRES_ACTION_BY.OPERATOR_MANAGER  # TODO not sure about this
        },
        'NCOE': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.MODERATE,
            'selectable_by': [LOG_ROLES.OPERATOR],
            'description': 'Case opened in error',
            'stops_timer': False
        },
        'CPTA': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [LOG_ROLES.OPERATOR],
            'description': 'Transfer back to Capita',
            'stops_timer': True,
            'set_requires_action_by': None_if_owned_by_operator
        }
    }
event_registry.register(SuspendCaseEvent)
