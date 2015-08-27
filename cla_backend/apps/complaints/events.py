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
            'type': LOG_TYPES.SYSTEM,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [],
            'description': u'Complaint created',
            'stops_timer': False,
        }),
        ('OWNER_SET', {
            'type': LOG_TYPES.SYSTEM,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [],
            'description': u'Complaint owner set',
            'stops_timer': False,
        }),
        ('COMPLAINT_NOTE', {
            'type': LOG_TYPES.SYSTEM,
            'level': LOG_LEVELS.MINOR,
            'selectable_by': [LOG_ROLES.OPERATOR],
            'description': u'Complaint note',
            'stops_timer': False,
        }),
        ('HOLDING_LETTER_SENT', {
            'type': LOG_TYPES.SYSTEM,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [LOG_ROLES.OPERATOR],
            'description': u'Complaint holding letter sent',
            'stops_timer': False,
        }),
        ('FULL_RESPONSE_SENT', {
            'type': LOG_TYPES.SYSTEM,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [LOG_ROLES.OPERATOR],
            'description': u'Complaint full response sent',
            'stops_timer': False,
        }),
        ('COMPLAINT_CLOSED', {
            'type': LOG_TYPES.SYSTEM,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [LOG_ROLES.OPERATOR],
            'description': u'Complaint closed',
            'stops_timer': False,
        }),
        ('COMPLAINT_REOPENED', {
            'type': LOG_TYPES.SYSTEM,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [],
            'description': u'Complaint reopened',
            'stops_timer': False,
        }),
    ])

    def __init__(self):
        super(ComplaintEvent, self).__init__()
        self.complaint = None

    def create_log(self, *args, **kwargs):
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
