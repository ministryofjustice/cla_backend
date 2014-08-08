from cla_eventlog.serializers import LogSerializerBase
from core.drf.fields import ThreePartDateField
from rest_framework import serializers

from core.serializers import UUIDSerializer, PartialUpdateExcludeReadonlySerializerMixin
from legalaid.serializers import EligibilityCheckSerializerBase, \
    IncomeSerializerBase, PropertySerializerBase, SavingsSerializerBase, \
    DeductionsSerializerBase, PersonSerializerBase, \
    PersonalDetailsSerializerBase, \
    CaseSerializerBase, ProviderSerializerBase, \
    OutOfHoursRotaSerializerBase, ExtendedUserSerializerBase, \
    ThirdPartyDetailsSerializerBase, AdaptationDetailsSerializerBase, \
    MatterTypeSerializerBase, MediaCodeSerializer

from .models import Operator


class PropertySerializer(PropertySerializerBase):

    class Meta(PropertySerializerBase.Meta):
        fields = ('value', 'mortgage_left', 'share', 'id', 'disputed', 'main')


class IncomeSerializer(IncomeSerializerBase):

    class Meta(IncomeSerializerBase.Meta):
        fields = ('earnings', 'other_income', 'self_employed',)


class SavingsSerializer(SavingsSerializerBase):

    class Meta(SavingsSerializerBase.Meta):
        fields = (
            'bank_balance',
            'investment_balance',
            'asset_balance',
            'credit_balance',
        )


class DeductionsSerializer(DeductionsSerializerBase):

    class Meta(DeductionsSerializerBase.Meta):
        fields = (
            'income_tax', 'national_insurance', 'maintenance',
            'childcare', 'mortgage', 'rent',
            'criminal_legalaid_contributions',
        )


class PersonSerializer(PersonSerializerBase):

    income = IncomeSerializer(required=False)
    savings = SavingsSerializer(required=False)
    deductions = DeductionsSerializer(required=False)

    class Meta(PersonSerializerBase.Meta):
        fields = (
            'income',
            'savings',
            'deductions',
        )


class EligibilityCheckSerializer(EligibilityCheckSerializerBase):
    property_set = PropertySerializer(allow_add_remove=True, many=True, required=False)
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


class PersonalDetailsSerializer(PersonalDetailsSerializerBase):

    dob = ThreePartDateField(required=False, source='date_of_birth')

    class Meta(PersonalDetailsSerializerBase.Meta):
        fields = (
            'reference', 'title', 'full_name', 'postcode', 'street',
            'mobile_phone', 'home_phone', 'email', 'dob',
            'ni_number', 'exempt_user', 'exempt_user_reason',
            'contact_for_research', 'safe_to_contact', 'vulnerable_user'
        )

class ThirdPartyPersonalDetailsSerializer(PersonalDetailsSerializerBase):
    class Meta(PersonalDetailsSerializerBase.Meta):
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


class AdaptationDetailsSerializer(AdaptationDetailsSerializerBase):
    class Meta(AdaptationDetailsSerializerBase.Meta):
        fields = (
                'bsl_webcam', 'minicom', 'text_relay', 'skype_webcam',
                'language', 'notes', 'reference', 'callback_preference'
        )


class LogSerializer(LogSerializerBase):

    class Meta(LogSerializerBase.Meta):
        fields = ('code',
                  'created_by',
                  'created',
                  'notes',
                  'type',
                  'level',
                  'timer'
        )

class MatterTypeSerializer(MatterTypeSerializerBase):

    category = serializers.SlugRelatedField(slug_field='code', read_only=True)

    class Meta(MatterTypeSerializerBase.Meta):
        fields = (
            'category',
            'code',
            'description',
            'level'
        )


class CaseSerializer(PartialUpdateExcludeReadonlySerializerMixin, CaseSerializerBase):
    LOG_SERIALIZER = LogSerializer

    eligibility_check = UUIDSerializer(slug_field='reference', required=False, read_only=True)

    personal_details = UUIDSerializer(required=False, slug_field='reference', read_only=True)
    thirdparty_details = UUIDSerializer(required=False, slug_field='reference', read_only=True)
    adaptation_details = UUIDSerializer(required=False, slug_field='reference', read_only=True)

    created = serializers.DateTimeField(read_only=True)
    modified = serializers.DateTimeField(read_only=True)
    created_by = serializers.CharField(read_only=True)
    provider = serializers.PrimaryKeyRelatedField(required=False, read_only=True)
    provider_notes = serializers.CharField(max_length=500, required=False, read_only=True)
    full_name = serializers.CharField(source='personal_details.full_name', read_only=True)
    eligibility_state = serializers.CharField(source='eligibility_check.state', read_only=True)
    diagnosis_state = serializers.CharField(source='diagnosis.state', read_only=True)
    billable_time = serializers.IntegerField(read_only=True)
    postcode = serializers.CharField(source='personal_details.postcode', read_only=True)
    rejected = serializers.SerializerMethodField('is_rejected')

    def is_rejected(self, case):
        try:
            return case.rejected == 1
        except:
            return False

    class Meta(CaseSerializerBase.Meta):
        fields = (
            'eligibility_check', 'personal_details', 'reference', 'created',
            'modified', 'created_by', 'provider', 'log_set',
            'notes', 'provider_notes', 'full_name', 'thirdparty_details',
            'adaptation_details', 'laa_reference', 'eligibility_state', 'billable_time',
            'matter_type1', 'matter_type2', 'requires_action_by', 'diagnosis', 'media_code',
            'postcode', 'diagnosis_state', 'rejected'
        )


class ProviderSerializer(ProviderSerializerBase):
    class Meta(ProviderSerializerBase.Meta):
        fields = ('name', 'id', 'short_code', 'telephone_frontdoor', 'telephone_backdoor')


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
