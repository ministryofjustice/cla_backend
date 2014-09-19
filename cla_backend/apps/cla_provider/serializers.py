from cla_common.constants import FEEDBACK_ISSUE
from rest_framework import serializers

from core.serializers import JSONField

from cla_eventlog.serializers import LogSerializerBase

from legalaid.serializers import \
    EligibilityCheckSerializerBase, \
    SavingsSerializerBase, PropertySerializerBase, \
    CaseSerializerFull, ProviderSerializerBase, \
    ExtendedUserSerializerBase, \
    AdaptationDetailsSerializerBase, IncomeSerializerBase, \
    DeductionsSerializerBase, PersonalDetailsSerializerFull, \
    ThirdPartyPersonalDetailsSerializerBase, \
    ThirdPartyDetailsSerializerBase, PersonSerializerBase, \
    FeedbackSerializerBase

from .models import Staff


class PropertySerializer(PropertySerializerBase):
    class Meta(PropertySerializerBase.Meta):
        fields = ('value', 'mortgage_left', 'share', 'id', 'disputed', 'main')


class IncomeSerializer(IncomeSerializerBase):
    class Meta(IncomeSerializerBase.Meta):
        fields = (
            'earnings', 'self_employment_drawings', 'benefits', 'tax_credits',
            'child_benefits', 'maintenance_received', 'pension',
            'other_income', 'self_employed', 'total'
        )


class PartnerIncomeSerializer(IncomeSerializerBase):
    """
    Like IncomeSerializer but without 'child_benefits'
    """
    class Meta(IncomeSerializerBase.Meta):
        fields = (
            'earnings', 'self_employment_drawings', 'benefits', 'tax_credits',
            'maintenance_received', 'pension',
            'other_income', 'self_employed', 'total'
        )


class SavingsSerializer(SavingsSerializerBase):
    class Meta(SavingsSerializerBase.Meta):
        fields = (
            'bank_balance', 'investment_balance',
            'asset_balance', 'credit_balance', 'total',
        )


class DeductionsSerializer(DeductionsSerializerBase):
    class Meta(DeductionsSerializerBase.Meta):
        fields = (
            'income_tax', 'national_insurance', 'maintenance',
            'childcare', 'mortgage', 'rent',
            'criminal_legalaid_contributions', 'total'
        )


class PersonalDetailsSerializer(PersonalDetailsSerializerFull):
    class Meta(PersonalDetailsSerializerFull.Meta):
        fields = (
            'reference', 'title', 'full_name', 'postcode', 'street',
            'mobile_phone', 'home_phone', 'email', 'dob',
            'ni_number',
            'contact_for_research', 'safe_to_contact', 'vulnerable_user'
        )


class ThirdPartyPersonalDetailsSerializer(ThirdPartyPersonalDetailsSerializerBase):
    class Meta(ThirdPartyPersonalDetailsSerializerBase.Meta):
        fields = (
            'reference', 'title', 'full_name', 'postcode', 'street',
            'mobile_phone', 'home_phone', 'email'
        )


class ThirdPartyDetailsSerializer(ThirdPartyDetailsSerializerBase):
    personal_details = ThirdPartyPersonalDetailsSerializer(required=True)

    class Meta(ThirdPartyDetailsSerializerBase.Meta):
        fields = (
            'reference', 'personal_details', 'pass_phrase', 'reason',
            'personal_relationship', 'personal_relationship_note',
            'spoke_to', 'no_contact_reason', 'organisation_name',
        )


class PersonSerializer(PersonSerializerBase):
    income = IncomeSerializer(required=False)
    savings = SavingsSerializer(required=False)
    deductions = DeductionsSerializer(required=False)

    class Meta(PersonSerializerBase.Meta):
        fields = (
            'income', 'savings', 'deductions',
        )


class PartnerPersonSerializer(PersonSerializer):
    """
        Like PersonSerializer but without child_benefits
    """
    income = PartnerIncomeSerializer(required=False)

    class Meta(PersonSerializer.Meta):
        pass


class EligibilityCheckSerializer(EligibilityCheckSerializerBase):
    property_set = PropertySerializer(
        allow_add_remove=True, many=True, required=False
    )
    you = PersonSerializer(required=False)
    partner = PartnerPersonSerializer(required=False)
    notes = serializers.CharField(max_length=500, required=False, read_only=True)
    disputed_savings = SavingsSerializer(required=False)

    class Meta(EligibilityCheckSerializerBase.Meta):
        fields = (
            'reference',
            'category',
            'your_problem_notes',
            'notes',
            'property_set',
            'you',
            'partner',
            'disputed_savings',
            'dependants_young',
            'dependants_old',
            'is_you_or_your_partner_over_60',
            'has_partner',
            'on_passported_benefits',
            'on_nass_benefits',
            'state'
        )


class ExtendedEligibilityCheckSerializer(EligibilityCheckSerializer):
    calculations = JSONField(read_only=True)

    class Meta(EligibilityCheckSerializer.Meta):
        fields = list(EligibilityCheckSerializer.Meta.fields) + [
            'calculations'
        ]


class LogSerializer(LogSerializerBase):
    class Meta(LogSerializerBase.Meta):
        fields = (
            'code',
            'created_by',
            'created',
            'notes',
            'type',
            'level',
            'timer',
            'patch'
        )


class CaseSerializer(CaseSerializerFull):
    notes = serializers.CharField(max_length=5000, required=False, read_only=True)

    class Meta(CaseSerializerFull.Meta):
        fields = (
            'eligibility_check', 'personal_details', 'reference', 'created',
            'modified', 'created_by', 'provider', 'provider_viewed',
            'notes', 'provider_notes', 'full_name', 'thirdparty_details',
            'adaptation_details', 'laa_reference', 'eligibility_state',
            'matter_type1', 'matter_type2', 'requires_action_by', 'diagnosis',
            'media_code', 'postcode', 'diagnosis_state',
            'exempt_user', 'exempt_user_reason', 'ecf_statement',
            'date_of_birth', 'category', 'outcome_code'
        )


class AdaptationDetailsSerializer(AdaptationDetailsSerializerBase):
    class Meta(AdaptationDetailsSerializerBase.Meta):
        fields = (
            'bsl_webcam', 'minicom', 'text_relay', 'skype_webcam',
            'language', 'notes', 'reference', 'callback_preference'
        )


class ProviderSerializer(ProviderSerializerBase):
    class Meta(ProviderSerializerBase.Meta):
        fields = ('name', 'id')


class StaffSerializer(ExtendedUserSerializerBase):
    provider = ProviderSerializer(read_only=True)

    class Meta(ExtendedUserSerializerBase.Meta):
        model = Staff
        fields = (
            'username', 'first_name', 'last_name', 'email', 'provider',
            'is_manager',
        )


class FeedbackSerializer(FeedbackSerializerBase):
    issue = serializers.ChoiceField(choices=FEEDBACK_ISSUE)
    comment = serializers.CharField(max_length=1024, required=False)
    class Meta(FeedbackSerializerBase.Meta):
        fields = (
            'reference',
            'provider',
            'case',
            'created_by',
            'comment',
            'justified',
            'resolved',
            'created',
            'modified',
            'issue',
        )

