# -*- coding: utf-8 -*-
from cla_eventlog import event_registry
from cla_eventlog.constants import LOG_TYPES, LOG_LEVELS, LOG_ROLES
from cla_eventlog.events import BaseEvent
from cla_eventlog.models import ComplaintLog


class ComplaintEvent(BaseEvent):
    key = 'complaint'
    codes = {
        'COMPLAINT_CREATED': {
            'type': LOG_TYPES.EVENT,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [LOG_ROLES.OPERATOR],
            'description': 'Complaint created',
            'stops_timer': False
        },
        'OWNER_SET': {
            'type': LOG_TYPES.EVENT,
            'level': LOG_LEVELS.MODERATE,
            'selectable_by': [LOG_ROLES.OPERATOR],
            'description': 'Owner set',
            'stops_timer': False
        },
        'HOLDING_LETTER_SENT': {
            'type': LOG_TYPES.EVENT,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [LOG_ROLES.OPERATOR],
            'description': 'Holding letter sent',
            'stops_timer': False,
        },
        'FULL_RESPONSE_SENT': {
            'type': LOG_TYPES.EVENT,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [LOG_ROLES.OPERATOR],
            'description': 'Full response sent',
            'stops_timer': False
        },
        'COMPLAINT_RESOLVED': {
            'type': LOG_TYPES.EVENT,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [LOG_ROLES.OPERATOR],
            'description': 'Complaint resolved',
            'stops_timer': False
        },
        'COMPLAINT_CLOSED': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [LOG_ROLES.OPERATOR],
            'description': 'Complaint closed',
            'stops_timer': False
        },
    }

    def create_log(self, **kwargs):
        return ComplaintLog(complaint=self.complaint, **kwargs)

    def process(self, *args, **kwargs):
        self.complaint = kwargs.pop('complaint', None)
        super(ComplaintEvent, self).process(*args, **kwargs)

    def get_log_code(self, case=None, **kwargs):
        return kwargs.get('action')


event_registry.register(ComplaintEvent)
