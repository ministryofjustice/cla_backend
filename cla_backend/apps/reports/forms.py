import os
from datetime import timedelta, time, datetime
from cla_eventlog import event_registry

from django import forms
from django.db import connection
from django.utils import timezone
from django.contrib.admin import widgets

from legalaid.utils import diversity

from cla_eventlog.constants import LOG_TYPES

from . import sql


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
            self._convert_date(
                self.cleaned_data['date_to'] + timedelta(days=1))
        )


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

    passphrase = forms.CharField(
        required=False,
        help_text='Optional. If not provided, the report will not include diversity data'
    )

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
            "Adjustments_TYP", "Adjustments_CallbackPreferred",
            "Adjustments_Skype",
            "Gender",
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
            "Welsh", "Language", "Outcome_Created_At",
            "Username", "Has_Third_Party"
        ]

    def get_queryset(self):
        passphrase = self.cleaned_data.get('passphrase')

        if passphrase:
            diversity_expression = "pgp_pub_decrypt(diversity, dearmor('{key}'), %s)::json".format(
                key=diversity.get_private_key()
            )
        else:
            diversity_expression = "%s as placeholder, '{}'::json"

        sql = self.query.format(
            diversity_expression=diversity_expression
        )
        sql_args = [passphrase] + list(self.date_range)

        cursor = connection.cursor()
        cursor.execute(sql, sql_args)
        self.description = cursor.description
        return cursor.fetchall()


class MIFeedbackExtract(SQLFileReport):
    QUERY_FILE = 'MIExtractByFeedback.sql'

    def get_headers(self):
        return [
            "LAA_Reference",
            "Date_Feedback_Created",
            "Feedback_Issue",
            "Feedback_Justified",
            "Feedback_Resolved",
            "Text_Output",
            "Category"
        ]


class MIAlternativeHelpExtract(SQLFileReport):
    QUERY_FILE = 'MIAlternativeHelp.sql'

    def get_headers(self):
        return [
            "Id",
            "Reference",
            "Laa_reference",
            "Category",
            "Created",
            "Code",
            "Notes",
            "F2F",
            "KB_Id"
        ]


class MIContactsPerCaseByCategoryExtract(SQLFileReport):
    QUERY_FILE = 'MIContactsPerCaseByCategory.sql'

    def get_headers(self):
        return [
            "Reference",
            "LAA_Reference",
            "outcome_count",
            "category",
            "created",
            "outcomes"
        ]

    def get_valid_outcomes(self):
        return event_registry.filter(stops_timer=True,
                                     type=LOG_TYPES.OUTCOME).keys()

    @property
    def params(self):
        return self.date_range + (self.get_valid_outcomes(),)

    def get_queryset(self):
        cursor = connection.cursor()
        cursor.execute(self.query, self.params)
        self.description = cursor.description
        return cursor.fetchall()


class MISurveyExtract(SQLFileReport):
    QUERY_FILE = 'MISurveyExtract.sql'

    def get_headers(self):
        return [
            'Hash_ID',
            'created',
            'modified',
            'full_name',
            'postcode',
            'street',
            'phone',
            'email',
            'date_of_birth',
            'ni_number',
            'contact_for_research',
            'safe_to_contact'
        ]


class MICB1Extract(SQLFileReport):
    QUERY_FILE = 'MICB1s.sql'

    def get_headers(self):
        return ['LAA_Reference',
                'Hash_ID_personal_details_captured',
                'Case_ID',
                'Provider_ID_if_allocated',
                'Law_Category_Name',
                'Date_Case_Created',
                'Last_Modified_Date',
                'Outcome_Code_Child',
                'Billable_Time',
                'Matter_Type_1',
                'Matter_Type_2',
                'User_ID',
                'Scope_Status',
                'Eligibility_Status',
                'Time_to_OS_Access',
                'Outcome_Created_At',
                'Username',
                'Requires_Action_At',
                'Log_Notes',
                'Time_to_view_after_requires_action_at',
                'Time_to_action_after_requires_action_at',
                'Time_to_view_after_requires_action_at_for_humans',
                'Time_to_action_after_requires_action_at_for_humans',
                'Next_Outcome']
