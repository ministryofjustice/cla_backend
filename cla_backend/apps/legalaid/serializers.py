from rest_framework import serializers

from cla_eventlog.constants import LOG_TYPES
from cla_eventlog.serializers import LogSerializerBase

from core.serializers import UUIDSerializer, ClaModelSerializer
from cla_provider.models import Provider, OutOfHoursRota

from cla_common.money_interval.models import MoneyInterval

from .models import Category, Property, EligibilityCheck, Income, \
    Savings, Deductions, Person, PersonalDetails, Case, \
    ThirdPartyDetails, AdaptationDetails



class CategorySerializerBase(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ('code', 'name', 'description')


class ProviderSerializerBase(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Provider


class OutOfHoursRotaSerializerBase(ClaModelSerializer):
    category = serializers.SlugRelatedField(slug_field='code')
    provider = serializers.PrimaryKeyRelatedField()

    class Meta:
        model = OutOfHoursRota


class PropertySerializerBase(ClaModelSerializer):
    class Meta:
        model = Property
        fields = ()

class TotalsModelSerializer(ClaModelSerializer):
    total_fields = set()
    total = serializers.SerializerMethodField('get_total')

    def get_total(self, obj):
        total = 0
        for f in self.total_fields:
            value = getattr(obj, f, 0)

            if isinstance(value, MoneyInterval):
                subtotal = value.as_monthly()
            else:
                subtotal = getattr(obj, f, 0)

            if subtotal != None:
                total += subtotal
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

class ThirdPartyDetailsSerializerBase(serializers.ModelSerializer):
    personal_details = PersonalDetailsSerializerBase(required=True)

    class Meta:
        model = ThirdPartyDetails
        fields = ()

class AdaptationDetailsSerializerBase(serializers.ModelSerializer):
    class Meta:
        model = AdaptationDetails
        fields = ()

class PersonSerializerBase(ClaModelSerializer):
    income = IncomeSerializerBase(required=False)
    savings = SavingsSerializerBase(required=False)
    deductions = DeductionsSerializerBase(required=False)

    class Meta:
        model = Person
        fields = ()


class EligibilityCheckSerializerBase(ClaModelSerializer):
    category = serializers.SlugRelatedField(slug_field='code', required=False)
    your_problem_notes = serializers.CharField(max_length=500, required=False)
    notes = serializers.CharField(max_length=500, required=False)
    property_set = PropertySerializerBase(allow_add_remove=True, many=True,
                                          required=False)
    you = PersonSerializerBase(required=False)
    partner = PersonSerializerBase(required=False)

    class Meta:
        model = EligibilityCheck
        fields = ()

    def save(self, **kwargs):
        obj = super(EligibilityCheckSerializerBase, self).save(**kwargs)
        obj.update_state()
        return obj

class CaseSerializerBase(ClaModelSerializer):

    LOG_SERIALIZER = LogSerializerBase

    eligibility_check = UUIDSerializer(slug_field='reference')
    personal_details = PersonalDetailsSerializerBase()
    notes = serializers.CharField(max_length=500, required=False)
    provider_notes = serializers.CharField(max_length=500, required=False)
    log_set = serializers.SerializerMethodField('get_log_set')
    in_scope = serializers

    def get_log_set(self, case):
        case_log = case.log_set.filter(type=LOG_TYPES.OUTCOME)
        serializer = self.LOG_SERIALIZER(instance=case_log, many=True, required=False, read_only=True)
        return serializer.data

    class Meta:
        model = Case
        fields = ()


class ExtendedUserSerializerBase(serializers.ModelSerializer):
    username = serializers.CharField(read_only=True, source='user.username')
    first_name = serializers.CharField(read_only=True,
                                       source='user.first_name')
    last_name = serializers.CharField(read_only=True, source='user.last_name')
    email = serializers.CharField(read_only=True, source='user.email')

    class Meta:
        fields = ()
