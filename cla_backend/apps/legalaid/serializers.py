from rest_framework import serializers

from core.serializers import UUIDSerializer

from .models import Category, EligibilityCheck, Property, Finance, \
    PersonalDetails, Case


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'description')


class PropertySerializer(serializers.ModelSerializer):

    class Meta:
        model = Property
        fields = ('value', 'equity', 'share', 'id')


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
            'self_employed'
        )


class EligibilityCheckSerializer(serializers.ModelSerializer):
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
            'dependants_old'
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
