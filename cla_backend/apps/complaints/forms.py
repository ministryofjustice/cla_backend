# -*- coding: utf-8 -*-
from django import forms
from cla_eventlog import event_registry
from cla_eventlog.constants import LOG_ROLES
from cla_eventlog.forms import EventSpecificLogForm


class ComplaintLogForm(EventSpecificLogForm):
    LOG_EVENT_KEY = 'complaint'
    NOTES_MANDATORY = True

    notes = forms.CharField(required=True, max_length=10000)
    resolved = forms.NullBooleanField(required=False)

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

    def clean_resolved(self):
        resolved = self.cleaned_data.get('resolved')
        if self.cleaned_data.get('event_code') == 'COMPLAINT_CLOSED' \
                and resolved not in (True, False):
            raise forms.ValidationError('Closing a complaint requires a resolution')
        return resolved

    def get_notes(self):
        event_code = self.get_event_code()
        event_cls = event_registry.get_event(self.LOG_EVENT_KEY)
        event_description = event_cls.codes[event_code]['description']
        notes = u'%s.\n%s' % (event_description,
                              super(ComplaintLogForm, self).get_notes())
        return notes.strip()

    def save(self, user):
        super(ComplaintLogForm, self).save(user)
        if self.cleaned_data.get('event_code') == 'COMPLAINT_CLOSED':
            self.complaint.resolved = self.cleaned_data.get('resolved')
            self.complaint.save()
            self.complaint.eod.case.complaint_flag = False
            self.complaint.eod.case.save()
