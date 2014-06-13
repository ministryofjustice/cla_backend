from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from core.serializers import UUIDSerializer
from cla_provider.models import Provider, OutOfHoursRota

from cla_common.money_interval.models import MoneyInterval
from cla_common.money_interval.serializers import MoneyIntervalModelSerializerMixin


from .models import Category, Property, EligibilityCheck, Income, \
    Savings, Deductions, Person, PersonalDetails, Case, CaseLog, CaseLogType


class CategorySerializerBase(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category


class CaseLogTypeSerializerBase(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CaseLogType
        fields = ('code', 'description')


class ProviderSerializerBase(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Provider

class OutOfHoursRotaSerializerBase(serializers.ModelSerializer):

    category = serializers.SlugRelatedField(slug_field='code')
    provider = serializers.PrimaryKeyRelatedField()

    class Meta:
        model = OutOfHoursRota


class PropertySerializerBase(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ()


class ClaModelSerializer(MoneyIntervalModelSerializerMixin, ModelSerializer):
    pass


class TotalsModelSerializer(ClaModelSerializer):
    total_fields = set()
    total = serializers.SerializerMethodField('get_total')

    def get_total(self, obj):
        total = 0
        for f in self.total_fields:
            value = getattr(obj, f, 0)

            if isinstance(value, MoneyInterval):
                total += value.as_monthly()
            else:
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
            'income_tax', 'national_insurance',
            'maintenance',
            'childcare',
            'mortgage', 'rent',

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


class CaseLogSerializerBase(serializers.ModelSerializer):
    class Meta:
        model = CaseLog
        fields = None


class CaseSerializerBase(serializers.ModelSerializer):
    eligibility_check = UUIDSerializer(slug_field='reference')
    personal_details = PersonalDetailsSerializerBase()
    notes = serializers.CharField(max_length=500, required=False)
    provider_notes = serializers.CharField(max_length=500, required=False)
    in_scope = serializers.BooleanField(required=False)

    class Meta:
        model = Case
        fields = ()


class ExtendedUserSerializerBase(serializers.ModelSerializer):
    username = serializers.CharField(read_only=True, source='user.username')
    first_name = serializers.CharField(read_only=True, source='user.first_name')
    last_name = serializers.CharField(read_only=True, source='user.last_name')
    email = serializers.CharField(read_only=True, source='user.email')

    class Meta:
        fields = ()
