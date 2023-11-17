import re
from cla_provider.models import Provider
import os
from datetime import timedelta, time, datetime, date

from django import forms
from django.db.transaction import atomic
from django.utils import timezone
from django.contrib.admin import widgets

from legalaid.utils import diversity
from cla_common.constants import EXPRESSIONS_OF_DISSATISFACTION
from cla_eventlog.constants import LOG_TYPES, LOG_LEVELS
from cla_eventlog import event_registry
from complaints.constants import SLA_DAYS
from knowledgebase.models import Article
from reports.widgets import MonthYearWidget
from checker.models import ReasonForContacting

from . import sql
from .utils import get_reports_cursor, set_local_time_for_query


class ConvertDateMixin(object):
    def _convert_date(self, d):
        d = datetime.combine(d, time(hour=0, minute=0))
        d = timezone.make_aware(d, timezone.get_current_timezone())
        return d


class ReportForm(ConvertDateMixin, forms.Form):
    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        super(ReportForm, self).__init__(*args, **kwargs)

    def get_headers(self):
        raise NotImplementedError

    def get_rows(self):
        for row in self.get_queryset():
            yield row

    def __iter__(self):
        yield self.get_headers()
        for row in self.get_rows():
            yield row

    def get_output(self):
        return list(self)


class DateRangeReportForm(ReportForm):
    date_from = forms.DateField(widget=widgets.AdminDateWidget)
    date_to = forms.DateField(widget=widgets.AdminDateWidget)

    max_date_range = None

    def clean(self):
        cleaned_data = super(DateRangeReportForm, self).clean()
        if "date_from" in self.cleaned_data and "date_to" in self.cleaned_data:
            # date_range will add an extra day onto to than that which is displayed,
            # use the values from the user
            from_input = self._convert_date(self.cleaned_data["date_from"])
            to_input = self._convert_date(self.cleaned_data["date_to"])
            if from_input > to_input:
                raise forms.ValidationError(
                    "'Date from' (%s) should be before or equal to 'Date to' (%s)"
                    % (from_input.strftime("%d/%m/%Y"), to_input.strftime("%d/%m/%Y"))
                )
            if self.max_date_range:
                from_, to = self.date_range
                delta = to - from_
                if delta > timedelta(days=self.max_date_range, hours=12):
                    raise forms.ValidationError(
                        "The date range (%s) should span "
                        "no more than %s working days" % (delta, str(self.max_date_range))
                    )
        return cleaned_data  # can be removed in django 1.7

    @property
    def date_range(self):
        return (
            self._convert_date(self.cleaned_data["date_from"]),
            self._convert_date(self.cleaned_data["date_to"] + timedelta(days=1)),
        )


def year_range(backward=0, forward=10):
    this_year = date.today().year
    return range(this_year - backward, this_year + forward)


class MonthRangeReportForm(ReportForm):
    date = forms.DateField(widget=MonthYearWidget(years=year_range(backward=4, forward=3)))

    @property
    def month(self):
        return self._convert_date(self.cleaned_data["date"])


class SQLFileReportMixin(object):
    def __init__(self, *args, **kwargs):
        super(SQLFileReportMixin, self).__init__(*args, **kwargs)
        path = os.path.join(sql.__path__[0], self.QUERY_FILE)
        with open(path, "r") as f:
            self.query = f.read()

    def get_sql_params(self):
        raise NotImplementedError()

    def get_queryset(self):
        return self.execute_query(self.query, self.get_sql_params())

    def execute_query(self, query, params):
        with atomic():
            cursor = get_reports_cursor()
            try:
                cursor.execute(set_local_time_for_query(query), params)
                self.description = cursor.description
                return cursor.fetchall()
            finally:
                cursor.close()


class SQLFileDateRangeReport(SQLFileReportMixin, DateRangeReportForm):
    def get_sql_params(self):
        return self.date_range


class SQLFileMonthRangeReport(SQLFileReportMixin, MonthRangeReportForm):
    def get_sql_params(self):
        return (self.month.date(),)


class MIProviderAllocationExtract(SQLFileDateRangeReport):
    QUERY_FILE = "MIProviderAllocation.sql"

    def get_headers(self):
        return ["category"] + self._get_provider_names()

    def _get_provider_names(self):
        regex = re.compile(r"[^ 0-9A-Za-z.-]+")
        return [re.sub(regex, "", p["name"]) for p in Provider.objects.all().order_by("id").values("name")]

    def get_sql_params(self):
        params = super(MIProviderAllocationExtract, self).get_sql_params()
        cols = '"%s" text' % '" text, "'.join(self.get_headers())
        return params + (cols,)

    def get_queryset(self):
        return self.execute_query(self.query % self.get_sql_params(), [])


class MIVoiceReport(SQLFileMonthRangeReport):
    QUERY_FILE = "MIVoiceReport.sql"

    def get_headers(self):
        return [
            "id",
            "created",
            "modified",
            "provider_id",
            "created_by_id",
            "LAA_Reference",
            "Client_Ref",
            "Account_Number",
            "First_Name",
            "Surname",
            "DOB",
            "Age_Range",
            "Gender",
            "Ethnicity",
            "Postcode",
            "Eligibility_Code",
            "Matter_Type_1",
            "Matter_Type_2",
            "Stage_Reached",
            "Outcome_Code",
            "Date_Opened",
            "Date_Closed",
            "Time_Spent",
            "Case_Costs",
            "Disability_Code",
            "Disbursements",
            "Travel_Costs",
            "Determination",
            "Suitable_For_Telephone_Advice",
            "Exceptional_Case_ref",
            "Exempted_Reason_Code",
            "Adaptations",
            "Signposting_or_Referral",
            "Media_Code",
            "Telephone_or_Online",
            "month",
            "Provider",
            "has_linked_case_in_system",
            "OS_BillableTime",
            "count_of_timers",
            "count_of_outcomes",
        ]


class MICaseExtract(SQLFileDateRangeReport):
    QUERY_FILE = "MIExtractByOutcome.sql"

    passphrase = forms.CharField(
        required=False, help_text="Optional. If not provided, the report will not include diversity data"
    )

    def get_headers(self):
        return [
            "LAA_Reference",
            "Hash_ID",
            "Case_ID",
            "Split_Check",
            "Split_Link_Case",
            "Provider_ID",
            "Category_Name",
            "Date_Case_Created",
            "Last_Modified_Date",
            "Outcome_Code_Child",
            "Billable_Time",
            "Cumulative_Time",
            "Matter_Type_1",
            "Matter_Type_2",
            "User_ID",
            "Scope_Status",
            "Eligibility_Status",
            "Adjustments_BSL",
            "Adjustments_LLI",
            "Adjustments_MIN",
            "Adjustments_TYP",
            "Adjustments_CallbackPreferred",
            "Adjustments_Skype",
            "Gender",
            "Ethnicity",
            "Age(Range)",
            "Religion",
            "Sexual_Orientation",
            "Disability",
            "Time_of_Day",
            "Reject_Reason",
            "Media_Code",
            "Contact_Type",
            "Call_Back_Request_Time",
            "Call_Back_Actioned_Time",
            "Time_to_OS_Access",
            "Time_to_SP_Access",
            "Residency_Test",
            "Repeat_Contact",
            "Referral_Agencies",
            "Complaint_Type",
            "Complaint_Date",
            "Complaint_Owner",
            "Complaint_Target",
            "Complaint_Subject",
            "Complaint_Classification",
            "Complaint_Outcome",
            "Agree_Feedback",
            "Exempt_Client",
            "Welsh",
            "Language",
            "Outcome_Created_At",
            "Username",
            "Has_Third_Party",
            "Time_to_OS_Action",
            "Organisation",
        ]

    def get_rows(self):
        for row in self.get_queryset():
            full_row = list(row)
            diversity_json = full_row.pop() or {}

            def insert_value(key, val):
                index = self.get_headers().index(key)
                full_row.insert(index, val)

            insert_value("Gender", diversity_json.get("gender"))
            insert_value("Ethnicity", diversity_json.get("ethnicity"))
            insert_value("Religion", diversity_json.get("religion"))
            insert_value("Sexual_Orientation", diversity_json.get("sexual_orientation"))
            insert_value("Disability", diversity_json.get("disability"))
            yield full_row

    def get_queryset(self):
        passphrase = self.cleaned_data.get("passphrase")

        if passphrase:
            diversity_expression = "pgp_pub_decrypt(pd.diversity, dearmor('{key}'), %s)::json".format(
                key=diversity.get_private_key()
            )
        else:
            diversity_expression = "%s as placeholder, '{}'::json"

        sql = self.query.format(diversity_expression=diversity_expression)
        sql_args = [passphrase] + list(self.date_range)
        return self.execute_query(sql, sql_args)


class MICaseExtractExtended(SQLFileDateRangeReport):
    QUERY_FILE = "MIExtractByOutcomeExtended.sql"

    passphrase = forms.CharField(
        required=False, help_text="Optional. If not provided, the report will not include diversity data"
    )

    def get_headers(self):
        return [
            "LAA_Reference",
            "Hash_ID",
            "Case_ID",
            "Split_Check",
            "Split_Link_Case",
            "Provider_ID",
            "Category_Name",
            "Date_Case_Created",
            "Last_Modified_Date",
            "Outcome_Code_Child",
            "Billable_Time",
            "Cumulative_Time",
            "Matter_Type_1",
            "Matter_Type_2",
            "User_ID",
            "Scope_Status",
            "Eligibility_Status",
            "Adjustments_BSL",
            "Adjustments_LLI",
            "Adjustments_MIN",
            "Adjustments_TYP",
            "Adjustments_CallbackPreferred",
            "Adjustments_Skype",
            "Gender",
            "Ethnicity",
            "Age(Range)",
            "Religion",
            "Sexual_Orientation",
            "Disability",
            "Time_of_Day",
            "Reject_Reason",
            "Media_Code",
            "Contact_Type",
            "Call_Back_Request_Time",
            "Call_Back_Actioned_Time",
            "Time_to_OS_Access",
            "Time_to_SP_Access",
            "Residency_Test",
            "Repeat_Contact",
            "Referral_Agencies",
            "Complaint_Type",
            "Complaint_Date",
            "Complaint_Owner",
            "Complaint_Target",
            "Complaint_Subject",
            "Complaint_Classification",
            "Complaint_Outcome",
            "Agree_Feedback",
            "Exempt_Client",
            "Welsh",
            "Language",
            "Outcome_Created_At",
            "Username",
            "Has_Third_Party",
            "Time_to_OS_Action",
            "Organisation",
            "Notes",
            "Provider Notes",
        ]

    def get_rows(self):
        for row in self.get_queryset():
            full_row = list(row)
            diversity_json = full_row.pop() or {}

            def insert_value(key, val):
                index = self.get_headers().index(key)
                full_row.insert(index, val)

            insert_value("Gender", diversity_json.get("gender"))
            insert_value("Ethnicity", diversity_json.get("ethnicity"))
            insert_value("Religion", diversity_json.get("religion"))
            insert_value("Sexual_Orientation", diversity_json.get("sexual_orientation"))
            insert_value("Disability", diversity_json.get("disability"))
            yield full_row

    def get_queryset(self):
        passphrase = self.cleaned_data.get("passphrase")

        if passphrase:
            diversity_expression = "pgp_pub_decrypt(pd.diversity, dearmor('{key}'), %s)::json".format(
                key=diversity.get_private_key()
            )
        else:
            diversity_expression = "%s as placeholder, '{}'::json"

        sql = self.query.format(diversity_expression=diversity_expression)
        sql_args = [passphrase] + list(self.date_range)
        return self.execute_query(sql, sql_args)


class CaseDemographicsReport(SQLFileDateRangeReport):
    QUERY_FILE = "CaseDemographicsReport.sql"

    passphrase = forms.CharField(
        required=False, help_text="Optional. If not provided, the report will not include diversity data"
    )

    def get_headers(self):
        return [
            "LAA_Reference",
            "Hash_ID",
            "Case_ID",
            "Provider_ID",
            "Category_Name",
            "Date_Case_Created",
            "Matter_Type_1",
            "Matter_Type_2",
            "Scope_Status",
            "Eligibility_Status",
            "Adjustments_BSL",
            "Adjustments_LLI",
            "Adjustments_MIN",
            "Adjustments_TYP",
            "Adjustments_CallbackPreferred",
            "Adjustments_Skype",
            "Gender",
            "Ethnicity",
            "Age(Range)",
            "Religion",
            "Sexual_Orientation",
            "Disability",
            "Media_Code",
            "Contact_Type",
            "Referral_Agencies",
            "Exempt_Client",
            "Welsh",
            "Language",
            "Outcome_Created_At",
            "Has_Third_Party",
            "Organisation",
            "Notes",
            "Provider Notes",
            "Adaptation Notes",
            "Vulnerable User",
            "Geographical_region",
        ]

    def get_rows(self):
        for row in self.get_queryset():
            full_row = list(row)
            diversity_json = full_row.pop() or {}

            def insert_value(key, val):
                index = self.get_headers().index(key)
                full_row.insert(index, val)

            insert_value("Gender", diversity_json.get("gender"))
            insert_value("Ethnicity", diversity_json.get("ethnicity"))
            insert_value("Religion", diversity_json.get("religion"))
            insert_value("Sexual_Orientation", diversity_json.get("sexual_orientation"))
            insert_value("Disability", diversity_json.get("disability"))
            yield full_row

    def get_queryset(self):
        passphrase = self.cleaned_data.get("passphrase")

        if passphrase:
            diversity_expression = "pgp_pub_decrypt(pd.diversity, dearmor('{key}'), %s)::json".format(
                key=diversity.get_private_key()
            )
        else:
            diversity_expression = "%s as placeholder, '{}'::json"

        sql = self.query.format(diversity_expression=diversity_expression)
        sql_args = [passphrase] + list(self.date_range)
        return self.execute_query(sql, sql_args)


class MIFeedbackExtract(SQLFileDateRangeReport):
    QUERY_FILE = "MIExtractByFeedback.sql"

    def get_headers(self):
        return [
            "LAA_Reference",
            "Date_Feedback_Created",
            "Feedback_Issue",
            "Feedback_Justified",
            "Feedback_Resolved",
            "Text_Output",
            "Category",
            "Provider name",
            "User email",
        ]


class MIDuplicateCaseExtract(SQLFileDateRangeReport):
    QUERY_FILE = "MIDuplicateCases.sql"

    def get_headers(self):
        return ["LAA_Reference", "Reference", "Category", "Created", "Full_name", "DOB", "Postcode"]


class MIAlternativeHelpExtract(SQLFileDateRangeReport):
    QUERY_FILE = "MIAlternativeHelp.sql"

    def get_headers(self):
        return ["Id", "Reference", "Laa_reference", "Category", "Created", "Code", "Notes", "F2F", "KB_Id"]


class MIContactsPerCaseByCategoryExtract(SQLFileDateRangeReport):
    QUERY_FILE = "MIContactsPerCaseByCategory.sql"

    def get_headers(self):
        return ["Reference", "LAA_Reference", "outcome_count", "category", "created", "outcomes"]

    def get_valid_outcomes(self):
        return event_registry.filter(stops_timer=True, type=LOG_TYPES.OUTCOME).keys()

    def get_sql_params(self):
        return self.date_range + (self.get_valid_outcomes(),)


class MISurveyExtract(SQLFileDateRangeReport):
    QUERY_FILE = "MISurveyExtract.sql"

    def get_headers(self):
        return [
            "Hash_ID",
            "created",
            "modified",
            "full_name",
            "postcode",
            "street",
            "phone",
            "email",
            "date_of_birth",
            "ni_number",
            "contact_for_research",
            "contact_for_research_via",
            "safe_to_contact",
            "Third Party Contact",
            "Case Refs",
            "Third Party Case Refs",
            "Organisation",
        ]


class MICB1Extract(SQLFileDateRangeReport):
    # This now only returns the information needed for SLA1, SLA2 is calculated slightly differently
    # so we split it out.
    QUERY_FILE = "MICB1sSLA1.sql"

    # currently sunday to sunday
    max_date_range = 8

    def get_now(self):
        return timezone.now()

    def get_headers(self):
        return [
            "LAA_Reference",
            "Hash_ID_personal_details_captured",
            "Case_ID",
            "Provider_ID_if_allocated",
            "Law_Category_Name",
            "Date_Case_Created",
            "Last_Modified_Date",
            "Outcome_Code_Child",
            "Matter_Type_1",
            "Matter_Type_2",
            "created_by_id",
            "Scope_Status",
            "Eligibility_Status",
            "Outcome_Created_At",
            "Username",
            "operator_first_view_after_cb1__created",
            "operator_first_log_after_cb1__created",
            "Next_Outcome",
            "callback_window_start",
            "callback_window_end",
            "missed_sla_1",
            "Source",
            "Code",
            "Organisation",
        ]

    def get_sql_params(self):
        from_date, to_date = self.date_range
        return {"from_date": from_date, "to_date": to_date, "now": self.get_now()}


class MICB1ExtractSLA2(SQLFileDateRangeReport):
    # This only returns the information needed for SLA2, this has been copied from the original
    # MICB1Extract and had SLA1 removed.
    QUERY_FILE = "MICB1sSLA2.sql"

    max_date_range = 8

    def get_now(self):
        return timezone.now()

    def get_headers(self):
        return [
            "LAA_Reference",
            "Hash_ID_personal_details_captured",
            "Case_ID",
            "Provider_ID_if_allocated",
            "Law_Category_Name",
            "Date_Case_Created",
            "Last_Modified_Date",
            "Outcome_Code_Child",
            "Matter_Type_1",
            "Matter_Type_2",
            "created_by_id",
            "Scope_Status",
            "Eligibility_Status",
            "Outcome_Created_At",
            "Username",
            "operator_first_view_after_cb1__created",
            "operator_first_log_after_cb1__created",
            "Next_Outcome",
            "callback_window_start",
            "callback_window_end",
            "missed_sla_2",
            "Source",
            "Code",
            "Organisation",
        ]

    def get_sql_params(self):
        from_date, to_date = self.date_range
        return {"from_date": from_date, "to_date": to_date, "now": self.get_now()}


class MICB1ExtractAgilisys(SQLFileDateRangeReport):
    QUERY_FILE = "MICB1sSLAAgilisys.sql"

    max_date_range = 3

    def get_headers(self):
        return [
            "LAA_Reference",
            "Hash_ID_personal_details_captured",
            "Case_ID",
            "Provider_ID_if_allocated",
            "Law_Category_Name",
            "Date_Case_Created",
            "Last_Modified_Date",
            "Outcome_Code_Child",
            "Matter_Type_1",
            "Matter_Type_2",
            "created_by_id",
            "Scope_Status",
            "Eligibility_Status",
            "Outcome_Created_At",
            "Username",
            "operator_first_view_after_cb1__created",
            "operator_first_log_after_cb1__created",
            "Next_Outcome",
            "requires_action_at",
            "sla_15",
            "sla_120",
            "sla_480",
            "is_over_sla_15",
            "is_over_sla_120",
            "is_over_sla_480",
            "Source",
            "Code",
            "sla_30",
            "is_over_sla_30",
            "Organisation",
        ]


class MIDigitalCaseTypesExtract(SQLFileDateRangeReport):
    QUERY_FILE = "MIDigitalCaseTypes.sql"

    def get_headers(self):
        return [
            "laa_reference",
            "case_ref",
            "contact_type",
            "case_created_by",
            "means_test_completed_online",
            "call_me_back_only",
            "scope_result",
            "means_test_result",
            "last_code_used",
            "date_case_created",
        ]


class MIEODReport(SQLFileDateRangeReport):
    QUERY_FILE = "MIEOD.sql"

    def get_headers(self):
        return [
            "LAA_Reference",
            "Case_Reference",
            "Case_Category",
            # 'EOD_Created',
            "EOD_Updated",
            "EOD_Category",
            "EOD_Notes",
            "Major",
            # 'Is_Escalated',
            # 'Is_Resolved',
            # 'Is_Justified',
            "Organisation",
        ]

    def _get_col_index(self, column_name):
        return self.get_headers().index(column_name)

    def get_rows(self):
        eod_choices = EXPRESSIONS_OF_DISSATISFACTION.CHOICES_DICT
        for row in self.get_queryset():
            category_col = self._get_col_index("EOD_Category")
            if not row[category_col] and not row[self._get_col_index("EOD_Notes")]:
                continue
            row = list(row)  # row is a tuple
            row[category_col] = row[category_col] and eod_choices.get(row[category_col], "Unknown") or "Not set"
            yield row


class ComplaintsReport(SQLFileDateRangeReport):
    QUERY_FILE = "Complaints.sql"

    def get_headers(self):
        return [
            "LAA reference",
            "Case reference",
            "Full name",
            "Case category",
            "Created by operator",
            "Operator manager owner",
            "Complaint method",
            "Complaint received",
            "Complaint category",
            "Holding letter sent",
            "Full response sent",
            "Major/minor",
            "Justified?",
            "Complaint closed",
            "Resolved?",
            "Within SLA?",
            "Organisation",
        ]

    def get_sql_params(self):
        from_date, to_date = self.date_range
        return {
            "from_date": from_date,
            "to_date": to_date,
            "major": LOG_LEVELS.HIGH,
            "minor": LOG_LEVELS.MINOR,
            "sla_days": "%d days" % SLA_DAYS,
        }


class MIOBIEEExportExtract(MonthRangeReportForm):
    passphrase = forms.CharField(
        help_text="This is required, the diversity passpharse is required to"
        " decrypt the diversity information that people have given "
        "to us. If not provided or wrong then the report will fail "
        "to generate."
    )


class MetricsReport(SQLFileDateRangeReport):
    QUERY_FILE = "metrics.sql"

    def get_sql_params(self):
        from_date, to_date = self.date_range
        return {"from_date": from_date, "to_date": to_date}

    def get_headers(self):
        return [
            "Date",
            "Diagnosis_total",
            "Scope_unknown",
            "Outofscope",
            "Scope_contact",
            "Inscope",
            "Eligibility_check_total",
            "Eligibility_check_unknown",
            "Eligibility_check_ineligible",
            "Eligibility_check_eligible",
            "Cases_total",
            "Cases_unknown",
            "Cases_ineligible",
            "Cases_eligible",
            "Time_total",
            "Time_unknown",
            "Time_ineligible",
            "Time_eligible",
            "Time_web_total",
            "Time_web_unknown",
            "Time_web_ineligible",
            "Time_web_eligible",
            "Time_phone_total",
            "Time_phone_unknown",
            "Time_phone_ineligible",
            "Time_phone_eligible",
        ]


class MIExtractCaseViewAuditLog(SQLFileDateRangeReport):
    QUERY_FILE = "MIExtractCaseAuditLog.sql"

    def get_sql_params(self):
        from_date, to_date = self.date_range
        return {"from_date": from_date, "to_date": to_date}

    def get_headers(self):
        return ["Case", "Action", "Operator", "Organisation", "Date"]


class MIExtractComplaintViewAuditLog(SQLFileDateRangeReport):
    QUERY_FILE = "MIExtractComplaintAuditLog.sql"

    def get_sql_params(self):
        from_date, to_date = self.date_range
        return {"from_date": from_date, "to_date": to_date}

    def get_headers(self):
        return ["Case", "Complaint Id", "Action", "Operator", "Organisation", "Date"]


class ReasonsForContactingReport(DateRangeReportForm):
    # initialise the dataset here and pass in the referrer...
    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.referrer = None
        super(ReportForm, self).__init__(*args, **kwargs)

    def get_data_set(self):
        from_date, to_date = self.date_range
        return ReasonForContacting.get_report_category_stats(
            start_date=from_date, end_date=to_date, referrer=self.referrer
        )["categories"]

    def get_rows(self):
        for reason in self.get_data_set():
            yield [
                reason["description"],
                reason["percentage"],
                reason["count"],
                reason["with_cases"],
                reason["without_cases"],
            ]

    def get_headers(self):
        return ["Description", "Percentage", "Count", "With cases", "Without cases"]


class ReasonsForContactingDisaggregated(SQLFileDateRangeReport):
    QUERY_FILE = "ReasonsForContactingReportDisaggregated.sql"

    def get_sql_params(self):
        from_date, to_date = self.date_range
        return {"from_date": from_date, "to_date": to_date}

    def get_headers(self):
        return [
            "RFC ID",
            "Case ID",
            "Contact Option",
            "Contact Reason/s",
            "Problem Notes",
            "BSL or Webcam",
            "Minicom",
            "Text Relay",
            "Skype/Webcam",
            "Language",
            "Other Communication Needs",
            "RFC Date",
        ]


class AllKnowledgeBaseArticles(ReportForm):
    def get_queryset(self):
        return Article.objects.prefetch_related("articlecategorymatrix_set__article_category", "telephonenumber_set")

    def get_rows(self):
        for article in self.get_queryset():
            telephone_numbers = article.telephonenumber_set.all()
            categories = article.articlecategorymatrix_set.all()
            yield [
                article.pk,
                article.created,
                article.modified,
                article.resource_type,
                article.service_name,
                article.service_tag,
                article.organisation,
                article.website,
                article.email,
                article.description,
                article.public_description,
                article.how_to_use,
                article.when_to_use,
                article.address,
                article.opening_hours,
                article.keywords,
                article.geographic_coverage,
                article.type_of_service,
                article.accessibility,
                get_from_nth(telephone_numbers, 1, "name"),
                get_from_nth(telephone_numbers, 1, "number"),
                get_from_nth(telephone_numbers, 2, "name"),
                get_from_nth(telephone_numbers, 2, "number"),
                get_from_nth(telephone_numbers, 3, "name"),
                get_from_nth(telephone_numbers, 3, "number"),
                get_from_nth(telephone_numbers, 4, "name"),
                get_from_nth(telephone_numbers, 4, "number"),
                get_from_nth(categories, 1, "article_category.name"),
                get_from_nth(categories, 1, "preferred_signpost"),
                get_from_nth(categories, 2, "article_category.name"),
                get_from_nth(categories, 2, "preferred_signpost"),
                get_from_nth(categories, 3, "article_category.name"),
                get_from_nth(categories, 3, "preferred_signpost"),
                get_from_nth(categories, 4, "article_category.name"),
                get_from_nth(categories, 4, "preferred_signpost"),
                get_from_nth(categories, 5, "article_category.name"),
                get_from_nth(categories, 5, "preferred_signpost"),
                get_from_nth(categories, 6, "article_category.name"),
                get_from_nth(categories, 6, "preferred_signpost"),
            ]

    def get_headers(self):
        return [
            "ID",
            "Created",
            "Modified",
            "Resource type",
            "Service name",
            "Service tag",
            "Organisation",
            "Website",
            "Email",
            "Description",
            "Public description",
            "How to use",
            "When to use",
            "Address",
            "Opening hours",
            "Keywords",
            "Geographic coverage",
            "Type of service",
            "Accessibility",
            "Tel 1 name",
            "Tel 1 number",
            "Tel 2 name",
            "Tel 2 number",
            "Tel 3 name",
            "Tel 3 number",
            "Tel 4 name",
            "Tel 4 number",
            "Category 1",
            "Preferred signpost for category 1",
            "Category 2",
            "Preferred signpost for category 2",
            "Category 3",
            "Preferred signpost for category 3",
            "Category 4",
            "Preferred signpost for category 4",
            "Category 5",
            "Preferred signpost for category 5",
            "Category 6",
            "Preferred signpost for category 6",
        ]


def get_from_nth(items, n, attribute):
    try:
        item = items[n - 1]
    except IndexError:
        return ""
    else:
        return get_recursively(item, attribute)


def get_recursively(item, attribute):
    attribute_parts = attribute.split(".")
    value = getattr(item, attribute_parts[0])
    remaining = ".".join(attribute_parts[1:])
    if remaining:
        return get_recursively(value, remaining)
    return value if value is not None else ""
