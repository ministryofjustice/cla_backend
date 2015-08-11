# -*- coding: utf-8 -*-
from cla_common.constants import REQUIRES_ACTION_BY
from cla_eventlog import event_registry
from cla_eventlog.constants import LOG_TYPES, LOG_LEVELS, LOG_ROLES
from cla_eventlog.events import BaseEvent


class ComplaintEvent(BaseEvent):
    key = 'complaint'
    codes = {
        'HOLDING_LETTER_SENT': {
            'type': LOG_TYPES.EVENT,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [LOG_ROLES.OPERATOR],
            'description': 'Holding letter sent',
            'stops_timer': False,
            'set_requires_action_by': REQUIRES_ACTION_BY.OPERATOR
        },
        'FULL_RESPONSE_SENT': {
            'type': LOG_TYPES.EVENT,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [LOG_ROLES.OPERATOR],
            'description': 'Full response sent',
            'stops_timer': False
        },
    }

    def get_log_code(self, case=None, **kwargs):
        my_param = kwargs.get('my_param')
        if my_param == 'something':
            return 'CODE1'
        return 'CODE2'


event_registry.register(ComplaintEvent)
