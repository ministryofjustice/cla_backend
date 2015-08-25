# -*- coding: utf-8 -*-
from django import forms
from cla_eventlog import event_registry
from cla_eventlog.constants import LOG_ROLES
from cla_eventlog.forms import EventSpecificLogForm


class ComplaintLogForm(EventSpecificLogForm):
    LOG_EVENT_KEY = 'complaint'
    NOTES_MANDATORY = True

    notes = forms.CharField(required=True, max_length=10000)

    @classmethod
    def get_operator_code_objects(cls):
        event_cls = event_registry.get_event(cls.LOG_EVENT_KEY)
        return [item
                for item in event_cls.codes.items()
                if LOG_ROLES.OPERATOR in item[1]['selectable_by']]

    def __init__(self, *args, **kwargs):
        self.complaint = kwargs.pop('complaint')
        super(ComplaintLogForm, self).__init__(
            *args, case=self.complaint.eod.case, **kwargs)

    def get_kwargs(self):
        kwargs = super(ComplaintLogForm, self).get_kwargs()
        kwargs['complaint'] = self.complaint
        return kwargs

    def get_event_code_choices(self):
        return [
            (code, details.get('description', code))
            for (code, details) in self.get_operator_code_objects()
        ]
