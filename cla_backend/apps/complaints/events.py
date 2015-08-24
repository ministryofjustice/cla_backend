# -*- coding: utf-8 -*-
from collections import OrderedDict
from cla_eventlog import event_registry
from cla_eventlog.constants import LOG_TYPES, LOG_LEVELS, LOG_ROLES
from cla_eventlog.events import BaseEvent
from cla_eventlog.models import ComplaintLog
from django.contrib.contenttypes.models import ContentType


class ComplaintEvent(BaseEvent):
    key = 'complaint'
    codes = OrderedDict([
        ('COMPLAINT_CREATED', {
            'type': LOG_TYPES.EVENT,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [LOG_ROLES.OPERATOR],
            'description': 'Complaint created',
            'stops_timer': False
        }),
        ('OWNER_SET', {
            'type': LOG_TYPES.EVENT,
            'level': LOG_LEVELS.MODERATE,
            'selectable_by': [LOG_ROLES.OPERATOR],
            'description': 'Owner set',
            'stops_timer': False
        }),
        ('HOLDING_LETTER_SENT', {
            'type': LOG_TYPES.EVENT,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [LOG_ROLES.OPERATOR],
            'description': 'Holding letter sent',
            'stops_timer': False,
        }),
        ('FULL_RESPONSE_SENT', {
            'type': LOG_TYPES.EVENT,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [LOG_ROLES.OPERATOR],
            'description': 'Full response sent',
            'stops_timer': False
        }),
        ('COMPLAINT_RESOLVED', {
            'type': LOG_TYPES.EVENT,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [LOG_ROLES.OPERATOR],
            'description': 'Complaint resolved',
            'stops_timer': False
        }),
        ('COMPLAINT_CLOSED', {
            'type': LOG_TYPES.OUTCOME,  # TODO: should this be LOG_TYPES.EVENT?
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [LOG_ROLES.OPERATOR],
            'description': 'Complaint closed',
            'stops_timer': False
        }),
    ])

    def __init__(self):
        super(ComplaintEvent, self).__init__()
        self.complaint = None

    def create_log(self, *args, **kwargs):
        if not self.complaint:
            return super(ComplaintEvent, self).create_log(*args, **kwargs)

        content_type = ContentType.objects.get_for_model(
            self.complaint.__class__)
        return ComplaintLog(
            object_id=self.complaint.pk,
            content_type=content_type,
            *args,
            **kwargs)

    def process(self, *args, **kwargs):
        self.complaint = kwargs.pop('complaint', None)
        return super(ComplaintEvent, self).process(*args, **kwargs)

    def get_log_code(self, case=None, **kwargs):
        return kwargs.get('code')


event_registry.register(ComplaintEvent)
