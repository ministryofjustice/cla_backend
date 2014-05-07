from legalaid.constants import CASELOGTYPE_SUBTYPES
from rest_framework import serializers

from cla_common.constants import CASE_STATE_CHOICES, CASE_STATE_OPEN

from legalaid.models import EligibilityCheck
from legalaid.serializers import UUIDSerializer, EligibilityCheckSerializerBase, \
    IncomeSerializerBase, PropertySerializerBase, SavingsSerializerBase, \
    DeductionsSerializerBase, PersonSerializerBase, PersonalDetailsSerializerBase, \
    CaseSerializerBase, CategorySerializerBase, ProviderSerializerBase, \
    CaseLogSerializerBase, CaseLogTypeSerializerBase


class CategorySerializer(CategorySerializerBase):
    class Meta(CategorySerializerBase.Meta):
        fields = ('code', 'name', 'description')


class CaseLogTypeSerializer(CaseLogTypeSerializerBase):
    class Meta(CaseLogTypeSerializerBase.Meta):
        fields = ('code', 'description')


class PropertySerializer(PropertySerializerBase):

    class Meta(PropertySerializerBase.Meta):
        fields = ('value', 'mortgage_left', 'share', 'id')


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
            'income_tax_and_ni', 'maintenance',
            'childcare', 'mortgage_or_rent',
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
            'state'
        )


class PersonalDetailsSerializer(PersonalDetailsSerializerBase):
    class Meta(PersonalDetailsSerializerBase.Meta):
        fields = (
            'title', 'full_name', 'postcode', 'street', 'town',
            'mobile_phone', 'home_phone'
        )


class CaseLogSerializer(CaseLogSerializerBase):
    code = serializers.CharField(read_only=True, source='logtype.code')
    created_by = serializers.CharField(read_only=True, source='created_by.username')
    created = serializers.DateTimeField(read_only=True)
    notes = serializers.CharField(read_only=True)

    class Meta(CaseLogSerializerBase.Meta):
        fields = ('code', 'created_by', 'created', 'notes')


class CaseSerializer(CaseSerializerBase):
    eligibility_check = UUIDSerializer(
            slug_field='reference',
            default=lambda: EligibilityCheck.objects.create().reference)

    personal_details = PersonalDetailsSerializer(required=False)

    created = serializers.DateTimeField(read_only=True)
    modified = serializers.DateTimeField(read_only=True)
    created_by = serializers.CharField(read_only=True)
    state = serializers.ChoiceField(choices=CASE_STATE_CHOICES, default=CASE_STATE_OPEN, read_only=True)
    provider = serializers.PrimaryKeyRelatedField(required=False, read_only=True)
    provider_notes = serializers.CharField(max_length=500, required=False, read_only=True)
    caseoutcome_set = serializers.SerializerMethodField('get_caseoutcome_set')

    def get_caseoutcome_set(self, case):
        case_outcomes = case.caselog_set.filter(logtype__subtype=CASELOGTYPE_SUBTYPES.OUTCOME)
        serializer = CaseLogSerializer(instance=case_outcomes, many=True, required=False, read_only=True)
        return serializer.data

    class Meta(CaseSerializerBase.Meta):
        fields = (
            'eligibility_check', 'personal_details',
            'reference', 'created', 'modified', 'created_by', 'state',
            'provider', 'caseoutcome_set', 'notes', 'provider_notes', 'in_scope'
        )


class ProviderSerializer(ProviderSerializerBase):
    class Meta(ProviderSerializerBase.Meta):
        fields = ('name', 'id', 'short_code')

