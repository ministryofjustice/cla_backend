from rest_framework import serializers

from core.serializers import UUIDSerializer

from .models import Category, EligibilityCheck, Property, Finance, \
    PersonalDetails, Case


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ('code', 'name', 'description')


class PropertySerializer(serializers.ModelSerializer):

    class Meta:
        model = Property
        fields = ('value', 'mortgage_left', 'share', 'id')


class FinanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Finance
        fields = (
            'bank_balance',
            'investment_balance',
            'asset_balance',
            'credit_balance',
            'earnings',
            'other_income',
            'self_employed',

            'income_tax_and_ni',
            'maintenance',
            'mortgage_or_rent',
            'criminal_legalaid_contributions'
        )


class EligibilityCheckSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field='code', required=False)
    your_problem_notes = serializers.CharField(max_length=500, required=False)
    notes = serializers.CharField(max_length=500, required=False)
    property_set = PropertySerializer(allow_add_remove=True, many=True, required=False)
    your_finances = FinanceSerializer(required=False)
    partner_finances = FinanceSerializer(required=False)

    class Meta:
        model = EligibilityCheck
        fields = (
            'reference',
            'category',
            'your_problem_notes',
            'notes',
            'property_set',
            'your_finances',
            'partner_finances',
            'dependants_young',
            'dependants_old',
            'is_you_or_your_partner_over_60',
            'has_partner',
            'on_passported_benefits',
        )


class PersonalDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalDetails
        fields = (
            'title', 'full_name', 'postcode', 'street', 'town',
            'mobile_phone', 'home_phone'
        )


class CaseSerializer(serializers.ModelSerializer):
    eligibility_check = UUIDSerializer(slug_field='reference')
    personal_details = PersonalDetailsSerializer()

    class Meta:
        model = Case
        fields = (
            'eligibility_check', 'personal_details', 'reference'
        )
