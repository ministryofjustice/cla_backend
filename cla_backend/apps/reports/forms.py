from datetime import timedelta, time, datetime

from django import forms
from django.db.models.sql.aggregates import Aggregate
from django.utils import timezone
from django.contrib.admin import widgets
from django.template.defaulttags import date

from cla_provider.models import Provider
from legalaid.models import Case


class ConvertDateMixin(object):
    def _convert_date(self, d):
        d = datetime.combine(d, time(hour=0, minute=0))
        d = timezone.make_aware(d, timezone.get_current_timezone())
        return d


class ReportForm(ConvertDateMixin, forms.Form):
    date_from = forms.DateField(widget=widgets.AdminDateWidget)
    date_to = forms.DateField(widget=widgets.AdminDateWidget)


class ProviderCaseClosure(ReportForm):
    provider = forms.ModelChoiceField(queryset=Provider.objects.active())

    def get_queryset(self):
        date_from = self._convert_date(self.cleaned_data['date_from'])
        date_to = self._convert_date(self.cleaned_data['date_to'] + timedelta(days=1))

        # return CaseLog.objects.filter(
        #     created__range=(date_from, date_to),
        #     logtype__subtype=CASELOGTYPE_SUBTYPES.OUTCOME,
        #     logtype__action_key__in=[
        #         CASELOGTYPE_ACTION_KEYS.PROVIDER_CLOSE_CASE,
        #         CASELOGTYPE_ACTION_KEYS.PROVIDER_REJECT_CASE
        #     ],
        #     case__provider=self.cleaned_data['provider'],
        # ).order_by('created').values_list(
        #     'case__reference', 'created', 'logtype__code',
        #     'case__eligibility_check__category__name'
        # )
        raise NotImplementedError()

    def get_headers(self):
        return ['Case #', 'Closure Date', 'Outcome Code', 'Law Categories']

    def get_rows(self):
        total = 0
        qs = self.get_queryset()
        for outcome_data in qs:
            total += 1
            local_dt = timezone.localtime(outcome_data[1])
            yield [
                outcome_data[0], date(local_dt, "d/m/o H:i"),
                outcome_data[2], outcome_data[3]
            ]

        yield []
        yield ['Total: %d' % total]


class OperatorCaseClosure(ReportForm):

    def get_queryset(self):
        date_from = self._convert_date(self.cleaned_data['date_from'])
        date_to = self._convert_date(self.cleaned_data['date_to'] + timedelta(days=1))
        raise NotImplementedError()
        # return CaseLog.objects.filter(
        #     created__range=(date_from, date_to),
        #     logtype=CaseLogType.objects.get(code='REFSP'),
        #     ).order_by('created').values_list(
        #     'case__reference', 'case__created', 'created', 'logtype__code', 'case__provider__name'
        # )

    def get_headers(self):
        return [
            'Case #', 'Call Started', 'Call Assigned', 'Duration (sec)',
            'Outcome Code', 'To Provider']

    def get_rows(self):
        call_count = 0
        call_total_time = 0
        qs = self.get_queryset()
        for outcome_data in qs:
            call_count += 1
            delta = (outcome_data[2] - outcome_data[1]).seconds
            call_total_time += delta
            yield [
                outcome_data[0],
                outcome_data[1].strftime('%d/%m/%Y %H:%M'),
                outcome_data[2].strftime('%d/%m/%Y %H:%M'),
                delta,
                outcome_data[3],
                outcome_data[4]
            ]

        average_call_time_in_sec = 0
        if call_count:
            average_call_time_in_sec = (call_total_time / call_count)

        yield []
        yield ['Total: %d' % call_count]
        yield ['Average Duration: %d' % average_call_time_in_sec]


class TotalDuration(Aggregate):
    """
    Custom aggregate function which calculates the total duration of associated
    timer_timers.
    """
    sql_function = ''
    sql_template = '''SUM(CASE
            WHEN timer_timer.stopped IS NOT NULL THEN
                EXTRACT(EPOCH FROM (timer_timer.stopped - timer_timer.created))
            WHEN timer_timer.created IS NOT NULL THEN
                EXTRACT(EPOCH FROM (now() - timer_timer.created))
            ELSE
                0
            END
        )'''

    def __init__(self, lookup, **extra):
        self.lookup = lookup
        self.extra = extra

    @property
    def _default_alias(self):
        return '%s__%s' % (self.lookup, self.__class__.__name__.lower())

    def add_to_query(self, query, alias, col, source, is_summary):
        super(TotalDuration, self).__init__(
            col, source, is_summary, **self.extra)
        query.aggregate_select[alias] = self


class OperatorCaseCreate(ReportForm):

    def get_queryset(self):
        date_from = self._convert_date(self.cleaned_data['date_from'])
        date_to = self._convert_date(
            self.cleaned_data['date_to'] + timedelta(days=1))
        return Case.objects.filter(
            created__range=(date_from, date_to),
            created_by__operator__isnull=False,
        ).order_by('created').annotate(duration=TotalDuration('timer')).values_list(
           'reference', 'created', 'duration')

    def get_headers(self):
        return ['Case #', 'Assigned', 'Duration']

    def get_rows(self):
        qs = self.get_queryset()
        count = 0
        total_time = 0
        for case in qs:
            count += 1
            total_time += case[2]
            yield [
                case[0],
                case[1],
                case[2]
            ]
        yield []
        yield ['Total: {0}'.format(count)]
        yield ['Average duration: {0}'.format(total_time / count)]


class OperatorAvgDuration(ReportForm):

    def get_queryset(self):
        pass

    def get_headers(self):
        return []

    def get_rows(self):
        yield []


class Reallocation(ReportForm):

    def get_queryset(self):
        pass

    def get_headers(self):
        return []

    def get_rows(self):
        yield []


class DuplicateMatters(ReportForm):

    def get_queryset(self):
        pass

    def get_headers(self):
        return []

    def get_rows(self):
        yield []
