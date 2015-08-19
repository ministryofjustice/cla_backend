# -*- coding: utf-8 -*-
from django import forms
from cla_eventlog import event_registry
from cla_eventlog.forms import EventSpecificLogForm


class ComplaintFormMixin(object):
    LOG_EVENT_KEY = 'complaint'
    NOTES_MANDATORY = True

    def __init__(self, *args, **kwargs):
        self.complaint = kwargs.pop('complaint')
        super(ComplaintFormMixin, self).__init__(
            *args, case=self.complaint.eod.case, **kwargs)

    def get_kwargs(self):
        kwargs = super(ComplaintFormMixin, self).get_kwargs()
        kwargs['complaint'] = self.complaint
        return kwargs


class BaseComplaintLogForm(ComplaintFormMixin, EventSpecificLogForm):
    notes = forms.CharField(required=True, max_length=10000)

    def get_event_code_choices(self):
        event = event_registry.get_event(self.get_event_key())()
        return [(code, code) for code in event.codes.keys()[2:]]
