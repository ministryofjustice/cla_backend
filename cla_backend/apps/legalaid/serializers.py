from legalaid.constants import CASELOGTYPE_SUBTYPES
from legalaid.fields import MoneyIntervalField
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, WritableField

from core.serializers import UUIDSerializer
from cla_provider.models import Provider, OutOfHoursRota

from cla_common.helpers import MoneyInterval
 
from django.utils.translation import ugettext as _


from .models import Category, Property, EligibilityCheck, Income, \
    Savings, Deductions, Person, PersonalDetails, Case, CaseLog, CaseLogType


class CategorySerializerBase(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category


class CaseLogTypeSerializerBase(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CaseLogType


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


class MoneyIntervalDRFField(WritableField):
    type_name = 'MoneyIntervalDRFField'
    type_label = 'moneyIntervalDRFField'
    form_field_class = MoneyIntervalField

    def field_to_native(self, obj, field_name):
 
        moneyIntervalField = getattr(obj, field_name)
        return {'interval_period' : moneyIntervalField.interval_period,
                'per_interval_value' : moneyIntervalField.per_interval_value,
                }

    def from_native(self, value):
        # TODO remove word earnings and find it as field
        if isinstance(value, dict):
            mi = MoneyInterval(value['interval_period'])
            mi.set_as_pennies(value['per_interval_value'])
        else:
            # TODO - remove - only here for mock test - temporary
            mi = MoneyInterval('per_month')
            mi.set_as_pennies(value)
        return mi


class ClaModelSerializer(ModelSerializer):
    def __init__(self, *args, **kwargs):
        # add a model serializer which is used throughout this project
        self.field_mapping[MoneyIntervalField] = MoneyIntervalDRFField
        super(ClaModelSerializer, self).__init__(*args, **kwargs)


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
