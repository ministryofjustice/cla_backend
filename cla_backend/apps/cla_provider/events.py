from cla_common.constants import REQUIRES_ACTION_BY

from cla_eventlog import event_registry
from cla_eventlog.constants import LOG_TYPES, LOG_LEVELS, LOG_ROLES
from cla_eventlog.events import BaseEvent


class RejectCaseEvent(BaseEvent):
    key = 'reject_case'
    codes = {
        'MIS-OOS': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [],
            'description': 'Misdiagnosed, out of scope',
            'stops_timer': False,
            'order': 10,
            'set_requires_action_by': None
        },
        'MIS-MEANS': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [],
            'description': 'Misdiagnosed, means test isn\'t correct',
            'stops_timer': False,
            'order': 20,
            'set_requires_action_by': None
        },
        'COI': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [LOG_ROLES.SPECIALIST],
            'description': 'Conflict of Interest',
            'stops_timer': False,
            'order': 30,
            'set_requires_action_by': REQUIRES_ACTION_BY.OPERATOR
        },
        'MIS': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [],
            'description': 'Misdiagnosed, assigned to wrong Specialist or another Specialist is dealing with client',
            'stops_timer': False,
            'order': 40,
            'set_requires_action_by': REQUIRES_ACTION_BY.OPERATOR
        },
    }

    def get_log_code(self, **kwargs):
        is_conflict = kwargs.get('is_conflict')

        if is_conflict:
            return 'COI'

        return super(RejectCaseEvent, self).get_log_code(**kwargs)
event_registry.register(RejectCaseEvent)


class AcceptCaseEvent(BaseEvent):
    key = 'accept_case'
    codes = {
        'SPOP': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [],
            'description': 'Case taken',
            'stops_timer': False,
            'set_requires_action_by': REQUIRES_ACTION_BY.PROVIDER
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
            'description': 'Closed SP Case',
            'stops_timer': False,
            'set_requires_action_by': None
        },
        'DREFER': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [],
            'description': 'Arranged an appointment with a F2F specialist',
            'stops_timer': False,
            'set_requires_action_by': None
        },
    }

    def get_log_code(self, **kwargs):
        is_debt_referral = kwargs.get('is_debt_referral')

        if is_debt_referral:
            return 'DREFER'

        return 'CLSP'
event_registry.register(CloseCaseEvent)


class ReopenCaseEvent(BaseEvent):
    key = 'reopen_case'
    codes = {
        'REOPEN': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [],
            'description': 'Reopened SP Case',
            'stops_timer': False
        }
    }
event_registry.register(ReopenCaseEvent)


class SplitCaseEvent(BaseEvent):
    key = 'split_case'
    codes = {
        'REF-EXT': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [],
            'description': 'Referred externally',
            'stops_timer': False
        },
        'REF-INT': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [],
            'description': 'Referred internally',
            'stops_timer': False
        },
        'REF-EXT_CREATED': {
            'type': LOG_TYPES.SYSTEM,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [],
            'description': "Split case created and referred externally",
            'stops_timer': False
        },
        'REF-INT_CREATED': {
            'type': LOG_TYPES.SYSTEM,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [],
            'description': "Split case created and referred internally",
            'stops_timer': False
        }
    }

    def process_split(self, case, code=None, notes="", created_by=None, patch=None, context=None, **kwargs):
        original_case = case.from_case

        code = self.get_log_code(**kwargs)
        log = self.process(
            case,
            code=code,
            notes=notes,
            created_by=created_by,
            patch=patch,
            context=context,
            **kwargs
        )

        system_code = self.get_system_log_code(**kwargs)
        self.process(
            original_case,
            code=system_code,
            notes=self.codes[system_code]['description'],
            created_by=created_by,
            patch=patch,
            context=context,
            **kwargs
        )
        return log

    def get_log_code(self, **kwargs):
        internal = kwargs.get('internal')

        if internal:
            return 'REF-INT'
        else:
            return 'REF-EXT'

    def get_system_log_code(self, **kwargs):
        internal = kwargs.get('internal')

        if internal:
            return 'REF-INT_CREATED'
        else:
            return 'REF-EXT_CREATED'
event_registry.register(SplitCaseEvent)
