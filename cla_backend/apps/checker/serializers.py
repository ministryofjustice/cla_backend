from rest_framework import serializers

from legalaid.serializers import UUIDSerializer, \
    EligibilityCheckSerializerBase, PropertySerializerBase, \
    PersonalDetailsSerializerBase, CaseSerializerBase, \
    IncomeSerializerBase, SavingsSerializerBase, \
    DeductionsSerializerBase, PersonSerializerBase, \
    AdaptationDetailsSerializerBase


class PropertySerializer(PropertySerializerBase):
    @property
    def errors(self):
        return super(PropertySerializer, self).errors

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
    property_set = PropertySerializer(allow_add_remove=True, many=True, required=False)
    you = PersonSerializer(required=False)
    partner = PartnerPersonSerializer(required=False)
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
            'title', 'full_name', 'postcode', 'street',
            'mobile_phone', 'home_phone', 'email'
        )


class AdaptationDetailsSerializer(AdaptationDetailsSerializerBase):
    class Meta(AdaptationDetailsSerializerBase.Meta):
        fields = (
            'bsl_webcam', 'minicom', 'text_relay', 'skype_webcam', 'language'
        )


class CaseSerializer(CaseSerializerBase):
    eligibility_check = UUIDSerializer(slug_field='reference')
    adaptation_details = AdaptationDetailsSerializer(required=False)
    personal_details = PersonalDetailsSerializer()
    requires_action_at = serializers.DateTimeField(required=False)

    class Meta(CaseSerializerBase.Meta):
        fields = (
            'eligibility_check', 'personal_details', 'reference',
            'requires_action_at', 'outcome_code', 'adaptation_details',
        )
