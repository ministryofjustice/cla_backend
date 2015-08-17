# -*- coding: utf-8 -*-
from django import forms
from django.utils import timezone
from cla_eventlog.forms import BaseCaseLogForm
from complaints.events import ComplaintEvent


class BaseComplaintForm(BaseCaseLogForm):
    LOG_EVENT_KEY = 'complaint'

    def __init__(self, *args, **kwargs):
        self.complaint = kwargs.pop('complaint')
        super(BaseComplaintForm, self).__init__(
            *args, case=self.complaint.eod.case, **kwargs)

    def get_requires_action_at(self):
        raise NotImplementedError()

    def get_kwargs(self):
        kwargs = super(BaseComplaintForm, self).get_kwargs()
        kwargs['complaint'] = self.complaint
        return kwargs

    def get_notes(self):
        dt = timezone.localtime(self.get_requires_action_at())
        return u"Complaint registered at {dt}. {notes}".format(
            dt=dt.strftime("%d/%m/%Y %H:%M"),
            notes=self.cleaned_data['notes'] or ""
        )


class BaseComplaintLogForm(BaseComplaintForm):
    notes = forms.CharField(required=True, max_length=10000)
    action = forms.ChoiceField(
        required=True,
        choices=ComplaintEvent.codes.keys()[2:])

    def get_notes(self):
        return self.cleaned_data['notes'] or ""

    def get_kwargs(self):
        kwargs = super(BaseComplaintLogForm, self).get_kwargs()
        kwargs['action'] = self.cleaned_data['action']
        return kwargs
