from cla_eventlog.serializers import LogSerializerBase
from rest_framework import serializers

from cla_common.constants import CASE_STATES

from legalaid.serializers import UUIDSerializer, EligibilityCheckSerializerBase, \
    IncomeSerializerBase, PropertySerializerBase, SavingsSerializerBase, \
    DeductionsSerializerBase, PersonSerializerBase, PersonalDetailsSerializerBase, \
    CaseSerializerBase, CategorySerializerBase,  \
    ProviderSerializerBase, \
    ExtendedUserSerializerBase

from .models import Staff

class CategorySerializer(CategorySerializerBase):
    class Meta(CategorySerializerBase.Meta):
        fields = ('code', 'name', 'description')


class PropertySerializer(PropertySerializerBase):

    class Meta(PropertySerializerBase.Meta):
        fields = ('value', 'mortgage_left', 'share', 'id')


class IncomeSerializer(IncomeSerializerBase):

    class Meta(IncomeSerializerBase.Meta):
        fields = ('earnings', 'other_income', 'self_employed', 'total')


class SavingsSerializer(SavingsSerializerBase):

    class Meta(SavingsSerializerBase.Meta):
        fields = (
            'bank_balance',
            'investment_balance',
            'asset_balance',
            'credit_balance',
            'total',
        )


class DeductionsSerializer(DeductionsSerializerBase):

    class Meta(DeductionsSerializerBase.Meta):
        fields = (
            'income_tax', 'national_insurance', 'maintenance',
            'childcare', 'mortgage', 'rent',
            'criminal_legalaid_contributions',
            'total',
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


    class Meta(EligibilityCheckSerializerBase.Meta):
        fields = (
            'reference',
            'category',
            'your_problem_notes',
            'notes',
            'property_set',
            'you',
            'partner',
            'dependants_young',
            'dependants_old',
            'is_you_or_your_partner_over_60',
            'has_partner',
            'on_passported_benefits',
            'on_nass_benefits',
            'state'
        )


class PersonalDetailsSerializer(PersonalDetailsSerializerBase):
    class Meta(PersonalDetailsSerializerBase.Meta):
        fields = (
            'title', 'full_name', 'postcode', 'street',
            'mobile_phone', 'home_phone'
        )


class LogSerializer(LogSerializerBase):

    class Meta(LogSerializerBase.Meta):
        fields = ('code',
                  'created_by',
                  'created',
                  'notes',
                  'level',
                  'type'
        )

class CaseSerializer(CaseSerializerBase):

    LOG_SERIALIZER = LogSerializer

    eligibility_check = UUIDSerializer(
            slug_field='reference')

    personal_details = PersonalDetailsSerializer(required=False)

    created = serializers.DateTimeField(read_only=True)
    modified = serializers.DateTimeField(read_only=True)
    created_by = serializers.CharField(read_only=True)
    state = serializers.ChoiceField(choices=CASE_STATES.CHOICES, default=CASE_STATES.OPEN)
    provider = serializers.PrimaryKeyRelatedField(required=False)
    locked_by = serializers.CharField(read_only=True)
    locked_at = serializers.DateTimeField(read_only=True)

    log_set = serializers.SerializerMethodField('get_log_set')


    class Meta(CaseSerializerBase.Meta):
        fields = (
            'eligibility_check', 'personal_details',
            'reference', 'created', 'modified', 'created_by', 'state',
            'provider', 'log_set', 'locked_by', 'locked_at',
            'notes', 'provider_notes', 'laa_reference'
        )

class ProviderSerializer(ProviderSerializerBase):
    class Meta(ProviderSerializerBase.Meta):
        fields = ('name', 'id')


class StaffSerializer(ExtendedUserSerializerBase):
    provider = ProviderSerializer(read_only=True)

    class Meta:
        model = Staff
        fields = (
            'username', 'first_name', 'last_name', 'email', 'provider',
            'is_manager'
        )
