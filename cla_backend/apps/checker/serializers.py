from legalaid.serializers import UUIDSerializer, EligibilityCheckSerializerBase, \
    IncomeSerializerBase, PropertySerializerBase, SavingsSerializerBase, \
    DeductionsSerializerBase, PersonSerializerBase, PersonalDetailsSerializerBase, \
    CaseSerializerBase, CategorySerializerBase
from rest_framework import serializers
from rest_framework.fields import IntegerField


class CategorySerializer(CategorySerializerBase):
    class Meta(CategorySerializerBase.Meta):
        fields = ('code', 'name', 'description')


class PropertySerializer(PropertySerializerBase):

    @property
    def errors(self):
        return super(PropertySerializer, self).errors

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
            'total'
        )

class DeductionsSerializer(DeductionsSerializerBase):

    class Meta(DeductionsSerializerBase.Meta):
        fields = (
            'income_tax_and_ni', 'maintenance',
            'childcare', 'mortgage_or_rent',
            'criminal_legalaid_contributions', 'total'
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
    # TODO: DRF doesn't validate, fields that aren't REQ'd = True
    # we need to figure out a way to deal with it

    # dependants_young = IntegerField(default=0)
    # dependants_old = IntegerField(default=0)

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
        )


class PersonalDetailsSerializer(PersonalDetailsSerializerBase):
    class Meta(PersonalDetailsSerializerBase.Meta):
        fields = (
            'title', 'full_name', 'postcode', 'street', 'town',
            'mobile_phone', 'home_phone'
        )


class CaseSerializer(CaseSerializerBase):
    eligibility_check = UUIDSerializer(slug_field='reference')
    personal_details = PersonalDetailsSerializer()
    class Meta(CaseSerializerBase.Meta):
        fields = (
            'eligibility_check', 'personal_details', 'reference',
        )
