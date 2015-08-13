# -*- coding: utf-8 -*-
from django.utils import timezone
from cla_eventlog.forms import BaseCaseLogForm


class BaseComplaintForm(BaseCaseLogForm):
    LOG_EVENT_KEY = 'complaint'

    def get_requires_action_at(self):
        raise NotImplementedError()

    def get_notes(self):
        dt = timezone.localtime(self.get_requires_action_at())
        return u"Complaint registered at {dt}. {notes}".format(
            dt=dt.strftime("%d/%m/%Y %H:%M"),
            notes=self.cleaned_data['notes'] or ""
        )
