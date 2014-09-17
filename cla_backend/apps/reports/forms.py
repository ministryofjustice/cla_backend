from datetime import timedelta, time, datetime

from django import forms
from django.db import connection
from django.db.models.aggregates import Avg, Count
from django.db.models.sql.aggregates import Aggregate
from django.utils import timezone
from django.contrib.admin import widgets
from django.template.defaulttags import date
from django.db import connection

from cla_eventlog.constants import LOG_LEVELS
from cla_provider.models import Provider
from legalaid.models import Case
from . import sql
import os


class ConvertDateMixin(object):
    def _convert_date(self, d):
        d = datetime.combine(d, time(hour=0, minute=0))
        d = timezone.make_aware(d, timezone.get_current_timezone())
        return d


class ReportForm(ConvertDateMixin, forms.Form):

    def get_headers(self):
        raise NotImplementedError

    def get_rows(self):
        for row in self.get_queryset():
            yield row

    def __iter__(self):
        yield self.get_headers()
        for row in self.get_rows():
            yield row


class DateRangeReportForm(ReportForm):
    date_from = forms.DateField(widget=widgets.AdminDateWidget)
    date_to = forms.DateField(widget=widgets.AdminDateWidget)

    @property
    def date_range(self):
        return (
            self._convert_date(self.cleaned_data['date_from']),
            self._convert_date(self.cleaned_data['date_to'] + timedelta(days=1))
        )


class ProviderCaseClosure(DateRangeReportForm):
    provider = forms.ModelChoiceField(queryset=Provider.objects.active())

    def get_queryset(self):

        # return CaseLog.objects.filter(
        #     created__range=self.date_range,
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


class OperatorCaseClosure(DateRangeReportForm):

    def get_queryset(self):
        raise NotImplementedError()
        # return CaseLog.objects.filter(
        #     created__range=self.date_range,
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


class ReportAggregate(Aggregate):
    sql_function = ''
    sql_template = ''

    def __init__(self, lookup, **extra):
        self.lookup = lookup
        self.extra = extra

    @property
    def _default_alias(self):
        return '%s__%s' % (self.lookup, self.__class__.__name__.lower())

    def add_to_query(self, query, alias, col, source, is_summary):
        super(ReportAggregate, self).__init__(
            col, source, is_summary, **self.extra)
        query.aggregate_select[alias] = self


class TotalDuration(ReportAggregate):
    """
    Custom aggregate function which calculates the total duration of associated
    timer_timers.
    """
    sql_template = '''SUM(CASE
            WHEN timer_timer.stopped IS NOT NULL THEN
                EXTRACT(EPOCH FROM (timer_timer.stopped - timer_timer.created))
            WHEN timer_timer.created IS NOT NULL THEN
                EXTRACT(EPOCH FROM (now() - timer_timer.created))
            ELSE
                0
            END
        )'''


class AvgDuration(Aggregate):
    sql_template = '({0} / COUNT(%(field)s))'.format(TotalDuration.sql_template)


class OperatorCaseCreate(DateRangeReportForm):

    def get_queryset(self):
        return Case.objects.filter(
            created__range=self.date_range,
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
            yield case
        yield []
        yield ['Total: {0}'.format(count)]
        if count:
            yield ['Average duration: {0}'.format(total_time / count)]


class CaseReport(DateRangeReportForm):

    def get_queryset(self):
        queryset = Case.objects.filter(created__range=self.date_range)
        queryset = queryset.order_by('created')
        queryset = queryset.annotate(duration=TotalDuration('timer'))
        return queryset.values_list(
            'reference', 'created', 'modified',
            'created_by__id',
            'locked_by__id', 'locked_at',
            'laa_reference',
            'diagnosis__state',
            'eligibility_check__category__name',
            'adaptation_details__bsl_webcam', 'adaptation_details__minicom',
            'adaptation_details__text_relay',
            'adaptation_details__skype_webcam', 'adaptation_details__language',
            'adaptation_details__callback_preference',
            'duration', 'billable_time',
            'matter_type1__code', 'matter_type2__code',
            'media_code__code',
            'personal_details__postcode',
            'provider__name')

    def get_headers(self):
        return [
            'Case #', 'Created', 'Modified',
            'Created by',
            'Locked by', 'Locked at',
            'LAA ref',
            'Diagnosis',
            'Law area',
            'BSL Webcam', 'Minicom', 'Text Relay', 'Skype', 'Language',
            'Callback',
            'Duration', 'Billable time',
            'Matter type 1', 'Matter type 2',
            'Media code',
            'Postcode',
            'Provider']

    def get_rows(self):
        count = 0
        for row in self.get_queryset():
            count += 1
            yield row
        yield []
        yield 'Total:', count


class NewCasesWithAdaptationCount(DateRangeReportForm):

    def get_queryset(self):
        qs = Case.objects.filter(
                created__range=self.date_range)
        qs = qs.values_list(
            'adaptation_details__bsl_webcam', 'adaptation_details__minicom',
            'adaptation_details__text_relay', 'adaptation_details__skype_webcam',
            'adaptation_details__callback_preference',
            'adaptation_details__language')
        qs = qs.annotate(num_cases=Count('reference'))
        qs = qs.order_by('-num_cases')
        return qs

    def get_headers(self):
        return [
            'BSL Webcam', 'Minicom', 'Text Relay', 'Skype Webcam',
                'Callback', 'Other language', 'Num cases']


class CaseVolumeAndAvgDurationByDay(DateRangeReportForm):

    def get_queryset(self):
        cursor = connection.cursor()
        cursor.execute('''
SELECT
    (DATE_TRUNC('day', legalaid_case.created)) AS created_day,
    legalaid_case.created_by_id AS operator,
    COUNT(legalaid_case.reference) AS num_cases,
    CASE
        WHEN COUNT(timer_timer.id) = 0 THEN
            0
        ELSE
            ROUND(SUM(
                CASE
                    WHEN timer_timer.stopped IS NOT NULL THEN
                        EXTRACT(EPOCH FROM (timer_timer.stopped - timer_timer.created))
                    WHEN timer_timer.created IS NOT NULL THEN
                        EXTRACT(EPOCH FROM (now() - timer_timer.created))
                    ELSE
                        0
                END
            ) / COUNT(timer_timer.id))
    END AS avg_duration
FROM
    legalaid_case
    LEFT OUTER JOIN timer_timer ON
        (legalaid_case.id = timer_timer.linked_case_id)
WHERE
    legalaid_case.created BETWEEN %s AND %s
GROUP BY
    DATE_TRUNC('day', legalaid_case.created),
    operator;
        ''', self.date_range)
        return cursor.fetchall()

    def get_headers(self):
        return [
            'Date', 'Operator', 'Num cases', 'Avg Duration']


class ReferredCasesByCategory(CaseReport):

    def get_queryset(self):
        qs = super(ReferredCasesByCategory, self).get_queryset()
        qs = qs.filter(provider__isnull=False)
        qs = qs.order_by('eligibility_check__category__name', 'provider__name')
        return qs


class AllocatedCasesNoOutcome(CaseReport):

    def get_queryset(self):
        qs = Case.objects.filter(created__range=self.date_range)
        qs = qs.order_by('created')
        qs = qs.annotate(duration=TotalDuration('timer'))
        qs = qs.extra(select={'outcome': '''
            (SELECT
                l.code
            FROM
                cla_eventlog_log l
            WHERE
                l.case_id = legalaid_case.id
                AND l.type = 'outcome'
                AND l.level = {high}
            ORDER BY
                created DESC
            LIMIT 1)
        '''.format(high=LOG_LEVELS.HIGH)})
        qs = qs.filter(provider__isnull=False)
        query = qs.query.sql_with_params()
        raise Exception(query)
        return qs.values_list(
            'reference', 'created', 'modified',
            'created_by__id',
            'locked_by__id', 'locked_at',
            'laa_reference',
            'diagnosis__state',
            'eligibility_check__category__name',
            'adaptation_details__bsl_webcam', 'adaptation_details__minicom',
            'adaptation_details__text_relay',
            'adaptation_details__skype_webcam', 'adaptation_details__language',
            'adaptation_details__callback_preference',
            'duration', 'billable_time',
            'matter_type1__code', 'matter_type2__code',
            'media_code__code',
            'personal_details__postcode',
            'provider__name',
            'outcome')

    def get_headers(self):
        headers = super(AllocatedCasesNoOutcome, self).get_headers()
        return headers + ['Outcome code']


class SQLFileReport(DateRangeReportForm):
    def __init__(self, *args, **kwargs):
        super(DateRangeReportForm, self).__init__(*args, **kwargs)
        path = os.path.join(sql.__path__[0], self.QUERY_FILE)
        with open(path, 'r') as f:
            self.query = f.read()

    def get_queryset(self):
        cursor = connection.cursor()
        cursor.execute(self.query, self.date_range)
        self.description = cursor.description
        return cursor.fetchall()

class MICaseExtract(SQLFileReport):
    QUERY_FILE = 'MIExtractByOutcome.sql'

    def get_headers(self):
        return [
            'LAA_Reference', 'Hash_ID',
            'Case_ID', "Split_Check",
            "Split_Link_Case", "Provider_ID",
            "Category_Name", "Date_Case_Created",
            "Last_Modified_Date", "Outcome_Code_Child",
            "Billable_Time", "Cumulative_Time",
            "Matter_Type_1", "Matter_Type_2",
            "User_ID", "Scope_Status",
            "Eligibility_Status", "Adjustments_BSL",
            "Adjustments_LLI", "Adjustments_MIN",
            "Adjustments_TYP", "Gender",
            "Ethnicity", "Age(Range)",
            "Religion", "Sexual_Orientation",
            "Disability", "Time_of_Day",
            "Reject_Reason", "Media_Code",
            "Contact_Type", "Call_Back_Request_Time",
            "Call_Back_Actioned_Time", "Time_to_OS_Access",
            "Time_to_SP_Access", "Residency_Test",
            "Repeat_Contact", "Referral_Agencies", "Complaint_Type",
            "Complaint_Date", "Complaint_Owner",
            "Complaint_Target", "Complaint_Subject",
            "Complaint_Classification", "Complaint_Outcome",
            "Agree_Feedback", "Exempt_Client",
        ]

class MIFeedbackExtract(SQLFileReport):
    QUERY_FILE = 'MIExtractByFeedback.sql'

    def get_headers(self):
        return [
            "LAA_Reference",
            "Date_Feedback_Created",
            "Feedback_Issue",
            "Feedback_Justified",
            "Feedback_Resolved",
            "Text_Output"
        ]



