from rest_framework import serializers

from cla_common.constants import FEEDBACK_ISSUE
from core.serializers import UUIDSerializer
from cla_eventlog.serializers import LogSerializerBase
from cla_eventlog import registry as event_registry

from legalaid.serializers import (
    EligibilityCheckSerializerBase,
    PropertySerializerBase,
    SavingsSerializerBase,
    CaseSerializerFull,
    ProviderSerializerBase,
    OutOfHoursRotaSerializerBase,
    ExtendedUserSerializerBase,
    AdaptationDetailsSerializerBase,
    IncomeSerializerBase,
    DeductionsSerializerBase,
    PersonalDetailsSerializerFull,
    ThirdPartyPersonalDetailsSerializerBase,
    ThirdPartyDetailsSerializerBase,
    PersonSerializerBase,
    FeedbackSerializerBase,
    CaseArchivedSerializerBase,
    CaseNotesHistorySerializerBase,
    CSVUploadSerializerBase,
    EODDetailsSerializerBase,
)

from .models import Operator
from legalaid.models import PersonalDetails


class PropertySerializer(PropertySerializerBase):
    class Meta(PropertySerializerBase.Meta):
        fields = ("value", "mortgage_left", "share", "id", "disputed", "main")


class IncomeSerializer(IncomeSerializerBase):
    self_employed = serializers.NullBooleanField(default=None)

    class Meta(IncomeSerializerBase.Meta):
        fields = (
            "earnings",
            "self_employment_drawings",
            "benefits",
            "tax_credits",
            "child_benefits",
            "maintenance_received",
            "pension",
            "other_income",
            "self_employed",
            "total",
        )


class PartnerIncomeSerializer(IncomeSerializerBase):
    """
    Like IncomeSerializer but without 'child_benefits'
    """

    self_employed = serializers.NullBooleanField(default=None)

    class Meta(IncomeSerializerBase.Meta):
        fields = (
            "earnings",
            "self_employment_drawings",
            "benefits",
            "tax_credits",
            "maintenance_received",
            "pension",
            "other_income",
            "self_employed",
            "total",
        )


class SavingsSerializer(SavingsSerializerBase):
    class Meta(SavingsSerializerBase.Meta):
        fields = ("bank_balance", "investment_balance", "asset_balance", "credit_balance", "total")


class DeductionsSerializer(DeductionsSerializerBase):
    class Meta(DeductionsSerializerBase.Meta):
        fields = (
            "income_tax",
            "national_insurance",
            "maintenance",
            "childcare",
            "mortgage",
            "rent",
            "criminal_legalaid_contributions",
            "total",
        )


class BarePersonalDetailsSerializer(PersonalDetailsSerializerFull):
    class Meta(PersonalDetailsSerializerFull.Meta):
        fields = ("reference", "full_name", "postcode", "dob")


class PersonalDetailsSerializer(PersonalDetailsSerializerFull):
    class Meta(PersonalDetailsSerializerFull.Meta):
        fields = (
            "reference",
            "title",
            "full_name",
            "postcode",
            "street",
            "mobile_phone",
            "home_phone",
            "email",
            "dob",
            "ni_number",
            "contact_for_research",
            "contact_for_research_methods",
            "safe_to_contact",
            "vulnerable_user",
            "has_diversity",
            "announce_call"
        )


class ThirdPartyPersonalDetailsSerializer(ThirdPartyPersonalDetailsSerializerBase):
    class Meta(ThirdPartyPersonalDetailsSerializerBase.Meta):
        fields = (
            "reference",
            "title",
            "full_name",
            "postcode",
            "street",
            "mobile_phone",
            "home_phone",
            "email",
            "safe_to_contact",
            "contact_for_research",
        )


class ThirdPartyDetailsSerializer(ThirdPartyDetailsSerializerBase):
    personal_details = ThirdPartyPersonalDetailsSerializer(required=True)

    class Meta(ThirdPartyDetailsSerializerBase.Meta):
        fields = (
            "reference",
            "personal_details",
            "pass_phrase",
            "reason",
            "personal_relationship",
            "personal_relationship_note",
            "spoke_to",
            "no_contact_reason",
            "organisation_name",
        )


class PersonSerializer(PersonSerializerBase):
    income = IncomeSerializer(required=False, allow_null=True)
    savings = SavingsSerializer(required=False, allow_null=True)
    deductions = DeductionsSerializer(required=False, allow_null=True)

    class Meta(PersonSerializerBase.Meta):
        fields = ("income", "savings", "deductions")


class PartnerPersonSerializer(PersonSerializer):
    """
        Like PersonSerializer but without child_benefits
    """

    income = PartnerIncomeSerializer(required=False, allow_null=True)

    class Meta(PersonSerializer.Meta):
        pass


class AdaptationDetailsSerializer(AdaptationDetailsSerializerBase):
    class Meta(AdaptationDetailsSerializerBase.Meta):
        fields = (
            "bsl_webcam",
            "minicom",
            "text_relay",
            "skype_webcam",
            "language",
            "notes",
            "reference",
            "callback_preference",
            "no_adaptations_required",
        )


class EODDetailsSerializer(EODDetailsSerializerBase):
    class Meta(EODDetailsSerializerBase.Meta):
        fields = ("categories", "notes", "reference")


class EligibilityCheckSerializer(EligibilityCheckSerializerBase):
    property_set = PropertySerializer(many=True, required=False)
    you = PersonSerializer(required=False, allow_null=True)
    partner = PartnerPersonSerializer(required=False, allow_null=True)
    notes = serializers.CharField(max_length=500, required=False, read_only=True)
    disputed_savings = SavingsSerializer(required=False, allow_null=True)

    class Meta(EligibilityCheckSerializerBase.Meta):
        fields = (
            "reference",
            "category",
            "your_problem_notes",
            "notes",
            "property_set",
            "you",
            "partner",
            "disputed_savings",
            "dependants_young",
            "dependants_old",
            "is_you_or_your_partner_over_60",
            "has_partner",
            "on_passported_benefits",
            "on_nass_benefits",
            "state",
            "specific_benefits",
            "disregards",
            "has_passported_proceedings_letter",
            "under_18_passported",
            "is_you_under_18",
            "under_18_receive_regular_payment",
            "under_18_has_valuables",
        )
        writable_nested_fields = ["you", "partner", "property_set", "disputed_savings"]


class LogSerializer(LogSerializerBase):
    description = serializers.SerializerMethodField()

    class Meta(LogSerializerBase.Meta):
        fields = ("code", "created_by", "created", "notes", "type", "level", "timer", "patch", "description")

    def get_description(self, log):
        return event_registry.event_registry.all().get(log.code, {}).get("description", "")


class CaseSerializer(CaseSerializerFull):
    provider_notes = serializers.CharField(max_length=10000, required=False, read_only=True)
    organisation = serializers.PrimaryKeyRelatedField(required=False, read_only=True)
    organisation_name = serializers.SerializerMethodField()
    billable_time = serializers.IntegerField(read_only=True)
    rejected = serializers.SerializerMethodField("is_rejected")
    callback_time_string = serializers.ReadOnlyField()

    complaint_count = serializers.IntegerField(read_only=True)

    def get_organisation_name(self, case):
        if not case.organisation:
            return

        return case.organisation.name

    def is_rejected(self, case):
        try:
            return case.rejected == 1
        except Exception:
            return False

    class Meta(CaseSerializerFull.Meta):
        fields = (
            "eligibility_check",
            "personal_details",
            "reference",
            "created",
            "modified",
            "created_by",
            "provider",
            "notes",
            "provider_notes",
            "full_name",
            "thirdparty_details",
            "adaptation_details",
            "laa_reference",
            "eligibility_state",
            "billable_time",
            "matter_type1",
            "matter_type2",
            "requires_action_by",
            "diagnosis",
            "media_code",
            "postcode",
            "diagnosis_state",
            "rejected",
            "date_of_birth",
            "category",
            "outcome_code",
            "outcome_description",
            "exempt_user",
            "exempt_user_reason",
            "ecf_statement",
            "case_count",
            "requires_action_at",
            "callback_time_string",
            "callback_attempt",
            "source",
            "complaint_flag",
            "eod_details",
            "call_started",
            "complaint_count",
            "organisation_name",
            "organisation",
        )


class CaseListSerializer(CaseSerializer):
    class Meta(CaseSerializer.Meta):
        fields = (
            "reference",
            "created",
            "modified",
            "full_name",
            "laa_reference",
            "eligibility_state",
            "personal_details",
            "requires_action_by",
            "postcode",
            "rejected",
            "date_of_birth",
            "category",
            "outcome_code",
            "outcome_description",
            "case_count",
            "source",
            "requires_action_at",
            "callback_time_string",
            "flagged_with_eod",
            "is_urgent",
            "organisation_name",
        )


class CreateCaseSerializer(CaseSerializer):
    """
    Case Serializer only used for creation.

    It allows the API to create a case with optional personal_details reference.
    No other fields can be used when creating a case atm.
    """

    personal_details = UUIDSerializer(
        slug_field="reference", required=False, queryset=PersonalDetails.objects.all(), allow_null=True
    )

    class Meta(CaseSerializer.Meta):
        fields = tuple(set(CaseSerializer.Meta.fields) - {"complaint_count"})
        writable_nested_fields = []


class ProviderSerializer(ProviderSerializerBase):
    class Meta(ProviderSerializerBase.Meta):
        fields = ("name", "id", "short_code", "telephone_frontdoor", "telephone_backdoor")


class OutOfHoursRotaSerializer(OutOfHoursRotaSerializerBase):
    provider_name = serializers.CharField(read_only=True, source="provider.name")

    class Meta(OutOfHoursRotaSerializerBase.Meta):
        fields = ("id", "start_date", "end_date", "category", "provider", "provider_name")


class OperatorSerializer(ExtendedUserSerializerBase):
    is_cla_superuser = serializers.BooleanField(read_only=True)

    class Meta(object):
        model = Operator
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "is_manager",
            "password",
            "created",
            "last_login",
            "is_cla_superuser",
            "organisation",
        )


class FeedbackSerializer(FeedbackSerializerBase):
    justified = serializers.BooleanField(required=False)
    resolved = serializers.BooleanField(required=False)
    issue = serializers.ChoiceField(choices=FEEDBACK_ISSUE, read_only=True)

    class Meta(FeedbackSerializerBase.Meta):
        fields = (
            "reference",
            "created_by",
            "case",
            "comment",
            "justified",
            "resolved",
            "provider",
            "created",
            "modified",
            "issue",
        )


class CaseArchivedSerializer(CaseArchivedSerializerBase):
    class Meta(CaseArchivedSerializerBase.Meta):
        fields = (
            "full_name",
            "date_of_birth",
            "postcode",
            "laa_reference",
            "specialist_referred_to",
            "date_specialist_referred",
            "date_specialist_closed",
            "knowledgebase_items_used",
            "area_of_law",
            "in_scope",
            "financially_eligible",
            "outcome_code",
            "outcome_code_date",
        )


class CaseNotesHistorySerializer(CaseNotesHistorySerializerBase):
    class Meta(CaseNotesHistorySerializerBase.Meta):
        fields = ("created_by", "created", "operator_notes", "provider_notes", "type_notes")


class CSVUploadSerializer(CSVUploadSerializerBase):
    class Meta(CSVUploadSerializerBase.Meta):
        fields = ["id", "provider", "created_by", "comment", "rows", "month", "created", "modified"]


class CSVUploadDetailSerializer(CSVUploadSerializerBase):
    class Meta(CSVUploadSerializerBase.Meta):
        fields = ["id", "provider", "created_by", "comment", "body", "month", "created", "modified"]
