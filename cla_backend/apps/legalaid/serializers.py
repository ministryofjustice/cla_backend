from legalaid.constants import CASELOGTYPE_SUBTYPES
from legalaid.fields import MoneyInterval
from rest_framework import serializers

from core.serializers import UUIDSerializer
from cla_provider.models import Provider

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


class PropertySerializerBase(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ()



from rest_framework.serializers import ModelSerializer, WritableField
from django.db.models import Field
from legalaid.fields import MoneyIntervalField
from django.utils.translation import ugettext as _

class MoneyIntervalsModelField(Field):
    #default_validators = [validators.validate_email]
    description = _("MoneyIntervalsModelField")
 
    def __init__(self, *args, **kwargs):
        # max_length should be overridden to 254 characters to be fully
        # compliant with RFCs 3696 and 5321
 
        #kwargs['max_length'] = kwargs.get('max_length', 75)
        Field.__init__(self, *args, **kwargs)
 
#     def formfield(self, **kwargs):
#         # As with CharField, this will cause email validation to be performed
#         # twice.
#         defaults = {
#             'form_class': forms.EmailField,
#         }
#         defaults.update(kwargs)
#         return super(EmailField, self).formfield(**defaults)
 
class MoneyIntervalDRFField(WritableField):
    type_name = 'MoneyIntervalDRFField'
    type_label = 'moneyIntervalDRFField'
    form_field_class = MoneyIntervalField
 
    default_error_messages = {
        'invalid': _('Enter a valid email address.'),
    }
#     default_validators = [validators.validate_email]
 
    def from_native(self, value):
        ret = super(MoneyIntervalDRFField, self).from_native(value)
        if ret is None:
            return None
        return ret.strip()


class TotalsModelSerializer(ModelSerializer):
    total_fields = set()

    total = serializers.SerializerMethodField('get_total')

    def __init__(self, *args, **kwargs):
        # add a model serializer which is used throughout this project
        self.field_mapping[MoneyIntervalsModelField] = MoneyIntervalDRFField
        super(TotalsModelSerializer, self).__init__(*args, **kwargs)


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
