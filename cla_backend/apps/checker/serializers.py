from django.conf import settings
from django.utils.functional import SimpleLazyObject
from rest_framework import serializers
from cla_common.constants import (
    CALLBACK_WINDOW_TYPES,
    CALLBACK_TYPES,
    FAST_TRACK_REASON,
    FINANCIAL_ASSESSMENT_STATUSES,
)
from diagnosis.graph import get_graph
from diagnosis.serializers import DiagnosisSerializer

from legalaid.serializers import (
    UUIDSerializer,
    EligibilityCheckSerializerBase,
    PropertySerializerBase,
    PersonalDetailsSerializerBase,
    CaseSerializerBase,
    IncomeSerializerBase,
    SavingsSerializerBase,
    DeductionsSerializerBase,
    PersonSerializerBase,
    AdaptationDetailsSerializerBase,
    ThirdPartyDetailsSerializerBase,
)
from legalaid.models import Case, EligibilityCheck
from checker.models import ReasonForContacting, ReasonForContactingCategory, ScopeTraversal
from core.serializers import ClaModelSerializer, JSONField

checker_graph = SimpleLazyObject(lambda: get_graph(file_name=settings.CHECKER_DIAGNOSIS_FILE_NAME))


class PropertySerializer(PropertySerializerBase):
    disputed = serializers.NullBooleanField(default=None)
    main = serializers.NullBooleanField(default=None)

    @property
    def errors(self):
        return super(PropertySerializer, self).errors

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

    income = PartnerIncomeSerializer(required=False, allow_null=True)

    class Meta(PersonSerializer.Meta):
        pass


class EligibilityCheckSerializer(EligibilityCheckSerializerBase):
    property_set = PropertySerializer(many=True, required=False, allow_null=True)
    you = PersonSerializer(required=False, allow_null=True)
    partner = PartnerPersonSerializer(required=False, allow_null=True)
    # TODO: DRF doesn't validate, fields that aren't REQ'd = True
    # we need to figure out a way to deal with it

    class Meta(EligibilityCheckSerializerBase.Meta):
        fields = (
            "reference",
            "category",
            "your_problem_notes",
            "notes",
            "property_set",
            "you",
            "partner",
            "dependants_young",
            "dependants_old",
            "is_you_or_your_partner_over_60",
            "has_partner",
            "on_passported_benefits",
            "on_nass_benefits",
            "specific_benefits",
            "disregards",
        )
        writable_nested_fields = ["you", "partner", "property_set"]


class PersonalDetailsSerializer(PersonalDetailsSerializerBase):
    class Meta(PersonalDetailsSerializerBase.Meta):
        fields = (
            "title",
            "full_name",
            "postcode",
            "street",
            "mobile_phone",
            "home_phone",
            "email",
            "safe_to_contact",
            "safe_to_email",
            "announce_call",
        )


class ThirdPartyDetailsSerializer(ThirdPartyDetailsSerializerBase):
    class Meta(ThirdPartyDetailsSerializerBase.Meta):
        fields = ("reference", "personal_details", "pass_phrase", "personal_relationship")


class AdaptationDetailsSerializer(AdaptationDetailsSerializerBase):
    class Meta(AdaptationDetailsSerializerBase.Meta):
        fields = ("bsl_webcam", "minicom", "text_relay", "skype_webcam", "language", "notes")


class ScopeTraversalSerializer(serializers.ModelSerializer):
    """ Can optionally be included when creating a Case via the checker case API route."""

    scope_answers = JSONField(required=False, allow_null=True)
    category = JSONField(required=False, allow_null=True)
    subcategory = JSONField(required=False, allow_null=True)
    financial_assessment_status = serializers.ChoiceField(required=False, choices=FINANCIAL_ASSESSMENT_STATUSES)
    fast_track_reason = serializers.ChoiceField(required=False, choices=FAST_TRACK_REASON)

    class Meta(object):
        fields = "__all__"
        model = ScopeTraversal


class CaseSerializer(CaseSerializerBase):
    eligibility_check = UUIDSerializer(
        slug_field="reference", required=False, queryset=EligibilityCheck.objects.all(), allow_null=True
    )
    adaptation_details = AdaptationDetailsSerializer(required=False, allow_null=True)
    personal_details = PersonalDetailsSerializer()
    thirdparty_details = ThirdPartyDetailsSerializer(required=False, allow_null=True)
    requires_action_at = serializers.DateTimeField(required=False, allow_null=True)
    callback_type = serializers.ChoiceField(required=False, choices=CALLBACK_TYPES)
    callback_window_type = serializers.ChoiceField(choices=CALLBACK_WINDOW_TYPES, required=False, allow_null=True)
    client_notes = serializers.CharField(required=False, allow_blank=True, max_length=5000)
    scope_traversal = ScopeTraversalSerializer(required=False, allow_null=True)

    class Meta(CaseSerializerBase.Meta):
        fields = (
            "eligibility_check",
            "personal_details",
            "reference",
            "requires_action_at",
            "callback_type",
            "callback_window_type",
            "adaptation_details",
            "thirdparty_details",
            "gtm_anon_id",
            "client_notes",
            "scope_traversal",
        )
        writable_nested_fields = ["adaptation_details", "personal_details", "thirdparty_details", "scope_traversal"]


class CheckerDiagnosisSerializer(DiagnosisSerializer):
    def _get_graph(self):
        return checker_graph


class ReasonForContactingCategorySerializer(serializers.ModelSerializer):
    class Meta(object):
        model = ReasonForContactingCategory
        fields = ("category",)


class ReasonForContactingSerializer(ClaModelSerializer):
    reasons = ReasonForContactingCategorySerializer(many=True, required=False)
    case = serializers.SlugRelatedField(
        slug_field="reference", read_only=False, required=False, queryset=Case.objects.all()
    )

    class Meta(object):
        model = ReasonForContacting
        fields = ("reference", "reasons", "other_reasons", "case", "referrer", "user_agent")
        writable_nested_fields = ["reasons"]
