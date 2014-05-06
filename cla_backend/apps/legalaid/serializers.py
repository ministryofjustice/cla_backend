from rest_framework import serializers

from core.serializers import UUIDSerializer
from cla_provider.models import Provider

from .models import Category, Property, EligibilityCheck, Income, \
    Savings, Deductions, Person, PersonalDetails, Case, OutcomeCode, CaseOutcome


class CategorySerializerBase(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category


class OutcomeCodeSerializerBase(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OutcomeCode

class ProviderSerializerBase(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Provider

class PropertySerializerBase(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ()

class TotalsModelSerializer(serializers.ModelSerializer):
    total_fields = set()

    total = serializers.SerializerMethodField('get_total')

    def get_total(self, obj):
        total = 0
        for f in self.total_fields:
            total += getattr(obj, f, 0)
        return total

class IncomeSerializerBase(TotalsModelSerializer):
    total_fields = {'earnings', 'other_income'}

    class Meta:
        model = Income
        fields = ()


class SavingsSerializerBase(TotalsModelSerializer):
    total_fields = \
        {'bank_balance',
         'investment_balance',
         'asset_balance',
         'credit_balance'}


    class Meta:
        model = Savings
        fields = ()


class DeductionsSerializerBase(TotalsModelSerializer):
    total_fields = \
        {
            'criminal_legalaid_contributions',
            'income_tax_and_ni',
            'maintenance',
            'childcare',
            'mortgage_or_rent',

        }

    class Meta:
        model = Deductions
        fields = ()


class PersonalDetailsSerializerBase(serializers.ModelSerializer):
    class Meta:
        model = PersonalDetails
        fields = ()


class PersonSerializerBase(serializers.ModelSerializer):
    income = IncomeSerializerBase(required=False)
    savings = SavingsSerializerBase(required=False)
    deductions = DeductionsSerializerBase(required=False)

    class Meta:
        model = Person
        fields = ()


class EligibilityCheckSerializerBase(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field='code', required=False)
    your_problem_notes = serializers.CharField(max_length=500, required=False)
    notes = serializers.CharField(max_length=500, required=False)
    property_set = PropertySerializerBase(allow_add_remove=True, many=True, required=False)
    you = PersonSerializerBase(required=False)
    partner = PersonSerializerBase(required=False)

    class Meta:
        model = EligibilityCheck
        fields = ()


class CaseOutcomeSerializerBase(serializers.ModelSerializer):
    class Meta:
        model = CaseOutcome
        fields = ()


class CaseSerializerBase(serializers.ModelSerializer):
    eligibility_check = UUIDSerializer(slug_field='reference')
    personal_details = PersonalDetailsSerializerBase()
    notes = serializers.CharField(max_length=500, required=False)
    provider_notes = serializers.CharField(max_length=500, required=False)
    in_scope = serializers.BooleanField(required=False)

    class Meta:
        model = Case
        fields = ()
