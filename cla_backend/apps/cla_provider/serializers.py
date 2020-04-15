from rest_framework import serializers

from cla_common.constants import FEEDBACK_ISSUE
from cla_eventlog.serializers import LogSerializerBase
from core.serializers import JSONField

from legalaid.serializers import (
    EligibilityCheckSerializerBase,
    SavingsSerializerBase,
    PropertySerializerBase,
    CaseSerializerFull,
    ProviderSerializerBase,
    ExtendedUserSerializerBase,
    AdaptationDetailsSerializerBase,
    IncomeSerializerBase,
    DeductionsSerializerBase,
    PersonalDetailsSerializerFull,
    ThirdPartyPersonalDetailsSerializerBase,
    ThirdPartyDetailsSerializerBase,
    PersonSerializerBase,
    FeedbackSerializerBase,
    CaseNotesHistorySerializerBase,
    CSVUploadSerializerBase,
)

from .models import Staff


class PropertySerializer(PropertySerializerBase):
    class Meta(PropertySerializerBase.Meta):
        fields = ("value", "mortgage_left", "share", "id", "disputed", "main")


class IncomeSerializer(IncomeSerializerBase):
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
            "safe_to_contact",
            "vulnerable_user",
            "has_diversity",
            "contact_for_research_methods",
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
    income = IncomeSerializer(required=False)
    savings = SavingsSerializer(required=False)
    deductions = DeductionsSerializer(required=False)

    class Meta(PersonSerializerBase.Meta):
        fields = ("income", "savings", "deductions")


class PartnerPersonSerializer(PersonSerializer):
    """
        Like PersonSerializer but without child_benefits
    """

    income = PartnerIncomeSerializer(required=False)

    class Meta(PersonSerializer.Meta):
        pass


class EligibilityCheckSerializer(EligibilityCheckSerializerBase):
    property_set = PropertySerializer(allow_add_remove=True, many=True, required=False)
    you = PersonSerializer(required=False)
    partner = PartnerPersonSerializer(required=False)
    notes = serializers.CharField(max_length=500, required=False, read_only=True)
    disputed_savings = SavingsSerializer(required=False)

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
            "has_passported_proceedings_letter",
        )


class ExtendedEligibilityCheckSerializer(EligibilityCheckSerializer):
    calculations = JSONField(read_only=True)

    class Meta(EligibilityCheckSerializer.Meta):
        fields = list(EligibilityCheckSerializer.Meta.fields) + ["calculations"]


class LogSerializer(LogSerializerBase):
    class Meta(LogSerializerBase.Meta):
        fields = ("code", "created_by", "created", "notes", "type", "level", "timer", "patch")


class CaseSerializer(CaseSerializerFull):
    notes = serializers.CharField(max_length=5000, required=False, read_only=True)

    provider_viewed = serializers.DateTimeField(read_only=True)
    provider_accepted = serializers.DateTimeField(read_only=True)
    provider_closed = serializers.DateTimeField(read_only=True)

    class Meta(CaseSerializerFull.Meta):
        fields = (
            "eligibility_check",
            "personal_details",
            "reference",
            "created",
            "modified",
            "created_by",
            "provider",
            "provider_viewed",
            "provider_accepted",
            "provider_closed",
            "notes",
            "provider_notes",
            "full_name",
            "thirdparty_details",
            "adaptation_details",
            "laa_reference",
            "eligibility_state",
            "matter_type1",
            "matter_type2",
            "requires_action_by",
            "diagnosis",
            "media_code",
            "postcode",
            "diagnosis_state",
            "exempt_user",
            "exempt_user_reason",
            "ecf_statement",
            "date_of_birth",
            "category",
            "outcome_code",
            "outcome_description",
            "source",
            "complaint_flag",
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
            "diagnosis_state",
            "date_of_birth",
            "category",
            "outcome_code",
            "outcome_description",
            "case_count",
            "provider_viewed",
            "provider_accepted",
            "provider_closed",
            "is_urgent",
        )


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


class ProviderSerializer(ProviderSerializerBase):
    class Meta(ProviderSerializerBase.Meta):
        fields = ("name", "id")


class StaffSerializer(ExtendedUserSerializerBase):
    provider = ProviderSerializer(read_only=True)

    chs_username = serializers.CharField(required=False)
    chs_organisation = serializers.CharField(required=False)
    chs_password = serializers.CharField(required=False, write_only=True)

    class Meta(ExtendedUserSerializerBase.Meta):
        model = Staff
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "provider",
            "is_manager",
            "password",
            "chs_password",
            "chs_organisation",
            "chs_user",
            "last_login",
            "created",
        )


class FeedbackSerializer(FeedbackSerializerBase):
    issue = serializers.ChoiceField(choices=FEEDBACK_ISSUE)
    comment = serializers.CharField(max_length=5000, required=False)

    class Meta(FeedbackSerializerBase.Meta):
        fields = (
            "reference",
            "provider",
            "case",
            "created_by",
            "comment",
            "justified",
            "resolved",
            "created",
            "modified",
            "issue",
        )


class CSVUploadSerializer(CSVUploadSerializerBase):

    body = JSONField(write_only=True)

    class Meta(CSVUploadSerializerBase.Meta):
        fields = ["id", "provider", "created_by", "comment", "rows", "body", "month", "created", "modified"]


class CSVUploadDetailSerializer(CSVUploadSerializerBase):
    class Meta(CSVUploadSerializerBase.Meta):
        fields = ["id", "provider", "created_by", "comment", "body", "month", "created", "modified"]


class CaseNotesHistorySerializer(CaseNotesHistorySerializerBase):
    class Meta(CaseNotesHistorySerializerBase.Meta):
        fields = ("created_by", "created", "operator_notes", "provider_notes", "type_notes")
