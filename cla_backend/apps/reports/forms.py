from datetime import timedelta, time, datetime

from django import forms
from django.utils import timezone
from django.contrib.admin import widgets

from cla_common.constants import CASE_STATE_CLOSED

from legalaid.models import CaseOutcome, OutcomeCode

from cla_provider.models import Provider


class ProviderCaseClosureReportForm(forms.Form):
    provider = forms.ModelChoiceField(queryset=Provider.objects.active())
    date_from = forms.DateField(widget=widgets.AdminDateWidget)
    date_to = forms.DateField(widget=widgets.AdminDateWidget)

    def _convert_date(self, d):
        d = datetime.combine(d, time(hour=0, minute=0))
        d = timezone.make_aware(d, timezone.get_current_timezone())
        return d

    def get_queryset(self):
        date_from = self._convert_date(self.cleaned_data['date_from'])
        date_to = self._convert_date(self.cleaned_data['date_to'] + timedelta(days=1))

        return CaseOutcome.objects.filter(
            created__range=(date_from, date_to),
            outcome_code__in=[oc.pk for oc in OutcomeCode.objects.filter(case_state=CASE_STATE_CLOSED)],
            case__provider=self.cleaned_data['provider'],
        ).order_by('created').values_list(
            'case__reference', 'created', 'outcome_code__code',
            'case__eligibility_check__category__name'
        )

    def get_headers(self):
        return ['Case #', 'Closure Date', 'Outcome Code', 'Law Categories']

    def get_rows(self):
        total = 0
        qs = self.get_queryset()
        for outcome_data in qs:
            total += 1
            yield [
                outcome_data[0], outcome_data[1].strftime('%d/%m/%Y %H:%M'),
                outcome_data[2], outcome_data[3]
            ]

        yield []
        yield ['Total: %d' % total]
