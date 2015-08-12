# -*- coding: utf-8 -*-
from django.utils import timezone
from cla_eventlog.forms import BaseCaseLogForm


class BaseComplaintForm(BaseCaseLogForm):
    LOG_EVENT_KEY = 'complaint'

    def get_requires_action_at(self):
        raise NotImplementedError()

    # def get_context(self):
    #     requires_action_at = self.get_requires_action_at()
    #
    #     _dt = timezone.localtime(requires_action_at)
    #     return {
    #         'requires_action_at': _dt,
    #         'sla_15': get_sla_time(_dt, 15),
    #         'sla_30': get_sla_time(_dt, 30),
    #         'sla_120': get_sla_time(_dt, 120),
    #         'sla_480': get_sla_time(_dt, 480)
    #     }

    def get_notes(self):
        dt = timezone.localtime(self.get_requires_action_at())
        return u"Complaint registered at {dt}. {notes}".format(
            dt=dt.strftime("%d/%m/%Y %H:%M"),
            notes=self.cleaned_data['notes'] or ""
        )

    # def save(self, user):
    #     super(BaseComplaintForm, self).save(user)
    #     dt = self.get_requires_action_at()
    #     self.case.set_requires_action_at(dt)
