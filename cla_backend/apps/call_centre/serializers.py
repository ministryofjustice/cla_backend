from rest_framework import serializers

from cla_eventlog.serializers import LogSerializerBase

from legalaid.serializers import EligibilityCheckSerializerBase, \
    PropertySerializerBase, SavingsSerializerBase, \
    CaseSerializerFull, ProviderSerializerBase, \
    OutOfHoursRotaSerializerBase, ExtendedUserSerializerBase, \
    AdaptationDetailsSerializerBase, IncomeSerializerBase, \
    DeductionsSerializerBase, PersonalDetailsSerializerFull, \
    ThirdPartyPersonalDetailsSerializerBase, \
    ThirdPartyDetailsSerializerBase, PersonSerializerBase, \
    FeedbackSerializerBase

from .models import Operator


class PropertySerializer(PropertySerializerBase):
    class Meta(PropertySerializerBase.Meta):
        fields = ('value', 'mortgage_left', 'share', 'id', 'disputed', 'main')


class IncomeSerializer(IncomeSerializerBase):
    class Meta(IncomeSerializerBase.Meta):
        fields = ('earnings', 'other_income', 'self_employed', 'total')


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


class AdaptationDetailsSerializer(AdaptationDetailsSerializerBase):
    class Meta(AdaptationDetailsSerializerBase.Meta):
        fields = (
            'bsl_webcam', 'minicom', 'text_relay', 'skype_webcam',
            'language', 'notes', 'reference', 'callback_preference'
        )


class EligibilityCheckSerializer(EligibilityCheckSerializerBase):
    property_set = PropertySerializer(
        allow_add_remove=True, many=True, required=False
    )
    you = PersonSerializer(required=False)
    partner = PersonSerializer(required=False)
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
    provider_notes = serializers.CharField(max_length=5000, required=False, read_only=True)
    billable_time = serializers.IntegerField(read_only=True)
    rejected = serializers.SerializerMethodField('is_rejected')

    def is_rejected(self, case):
        try:
            return case.rejected == 1
        except:
            return False

    class Meta(CaseSerializerFull.Meta):
        fields = (
            'eligibility_check', 'personal_details', 'reference', 'created',
            'modified', 'created_by', 'provider',
            'notes', 'provider_notes', 'full_name', 'thirdparty_details',
            'adaptation_details', 'laa_reference', 'eligibility_state',
            'billable_time', 'matter_type1', 'matter_type2',
            'requires_action_by', 'diagnosis',
            'media_code', 'postcode', 'diagnosis_state', 'rejected',
            'date_of_birth', 'category',
            'exempt_user', 'exempt_user_reason',
            'ecf_statement'
        )


class ProviderSerializer(ProviderSerializerBase):
    class Meta(ProviderSerializerBase.Meta):
        fields = (
            'name', 'id', 'short_code', 'telephone_frontdoor',
            'telephone_backdoor'
        )


class OutOfHoursRotaSerializer(OutOfHoursRotaSerializerBase):
    provider_name = serializers.CharField(read_only=True, source='provider.name')

    class Meta(OutOfHoursRotaSerializerBase.Meta):
        fields = (
            'id',
            'start_date',
            'end_date',
            'category',
            'provider',
            'provider_name',
        )


class OperatorSerializer(ExtendedUserSerializerBase):
    class Meta:
        model = Operator
        fields = (
            'username', 'first_name', 'last_name', 'email', 'is_manager'
        )

class FeedbackSerializer(FeedbackSerializerBase):
    justified = serializers.BooleanField(required=False)
    resolved = serializers.BooleanField(required=False)

    class Meta(FeedbackSerializerBase.Meta):
        fields = (
            'reference',
            'created_by',
            'case',
            'comment',
            'justified',
            'resolved',
            'provider',
            'created',
            'modified',
        )
