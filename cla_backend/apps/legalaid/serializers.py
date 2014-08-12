from rest_framework import serializers

from core.drf.fields import ThreePartDateField
from core.serializers import UUIDSerializer, ClaModelSerializer, \
    PartialUpdateExcludeReadonlySerializerMixin

from cla_common.constants import MATTER_TYPE_LEVELS
from cla_common.money_interval.models import MoneyInterval

from cla_eventlog.constants import LOG_LEVELS
from cla_eventlog.serializers import LogSerializerBase

from cla_provider.models import Provider, OutOfHoursRota

from .models import Category, Property, EligibilityCheck, Income, \
    Savings, Deductions, Person, PersonalDetails, Case, \
    ThirdPartyDetails, AdaptationDetails, MatterType, MediaCode, MediaCodeGroup


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


class PersonalDetailsSerializerFull(PersonalDetailsSerializerBase):
    dob = ThreePartDateField(required=False, source='date_of_birth')

    class Meta(PersonalDetailsSerializerBase.Meta):
        fields = ()


class ThirdPartyPersonalDetailsSerializerBase(PersonalDetailsSerializerBase):
    class Meta(PersonalDetailsSerializerBase.Meta):
        fields = ()


class ThirdPartyDetailsSerializerBase(serializers.ModelSerializer):
    personal_details = ThirdPartyPersonalDetailsSerializerBase(required=True)

    class Meta:
        model = ThirdPartyDetails
        fields = ()


class PersonSerializerBase(ClaModelSerializer):
    income = IncomeSerializerBase(required=False)
    savings = SavingsSerializerBase(required=False)
    deductions = DeductionsSerializerBase(required=False)

    class Meta:
        model = Person
        fields = ()


class AdaptationDetailsSerializerBase(serializers.ModelSerializer):
    bsl_webcam = serializers.BooleanField(label="BSL - Webcam", required=False)
    minicom = serializers.BooleanField(label="Minicom", required=False)
    text_relay = serializers.BooleanField(label="Text relay", required=False)
    skype_webcam = serializers.BooleanField(label="Skype", required=False)
    callback_preference = serializers.BooleanField(
        label="Callback preference", required=False
    )

    class Meta:
        model = AdaptationDetails
        fields = ()


class EligibilityCheckSerializerBase(ClaModelSerializer):
    property_set = PropertySerializerBase(
        allow_add_remove=True, many=True, required=False
    )
    you = PersonSerializerBase(required=False)
    partner = PersonSerializerBase(required=False)
    category = serializers.SlugRelatedField(slug_field='code', required=False)
    your_problem_notes = serializers.CharField(max_length=500, required=False)
    notes = serializers.CharField(max_length=500, required=False)

    class Meta:
        model = EligibilityCheck
        fields = ()

    def validate_property_set(self, attrs, source):
        """
        Checks that only one main property is selected
        """
        if source in attrs:
            main_props = [prop for prop in attrs[source] if prop.main]

            if len(main_props) > 1:
                raise serializers.ValidationError("Only one main property allowed")
        return attrs

    def save(self, **kwargs):
        obj = super(EligibilityCheckSerializerBase, self).save(**kwargs)
        obj.update_state()
        diff = obj.diff
        if 'category' in diff:
            # if the category has been updated then reset mattertype on
            # corresponding case
            obj.reset_matter_types()
        return obj


class MatterTypeSerializerBase(ClaModelSerializer):
    category = serializers.SlugRelatedField(slug_field='code', read_only=True)

    class Meta:
        model = MatterType
        fields = (
            'category', 'code', 'description', 'level'
        )


class MediaCodeSerializerBase(ClaModelSerializer):
    group = serializers.SlugRelatedField(slug_field='name', read_only=True)

    class Meta:
        model = MediaCode
        fields = (
            'group', 'name', 'code'
        )


class CaseSerializerBase(ClaModelSerializer, PartialUpdateExcludeReadonlySerializerMixin):
    LOG_SERIALIZER = LogSerializerBase

    eligibility_check = UUIDSerializer(slug_field='reference', read_only=True)
    diagnosis = UUIDSerializer(slug_field='reference', required=False, read_only=True)
    personal_details = PersonalDetailsSerializerBase()
    notes = serializers.CharField(max_length=500, required=False)
    provider_notes = serializers.CharField(max_length=500, required=False)
    log_set = serializers.SerializerMethodField('get_log_set')
    matter_type1 = serializers.SlugRelatedField(slug_field='code', required=False, queryset=MatterType.objects.filter(level=MATTER_TYPE_LEVELS.ONE))
    matter_type2 = serializers.SlugRelatedField(slug_field='code', required=False, queryset=MatterType.objects.filter(level=MATTER_TYPE_LEVELS.TWO))
    media_code = serializers.SlugRelatedField(slug_field='code', required=False)

    def get_log_set(self, case):
        case_log = case.log_set.filter(level__gt=LOG_LEVELS.MINOR)
        serializer = self.LOG_SERIALIZER(instance=case_log, many=True, required=False, read_only=True)
        return serializer.data

    class Meta:
        model = Case
        fields = ()


class CaseSerializerFull(CaseSerializerBase):
    eligibility_check = UUIDSerializer(slug_field='reference', required=False, read_only=True)

    personal_details = UUIDSerializer(required=False, slug_field='reference', read_only=True)
    thirdparty_details = UUIDSerializer(required=False, slug_field='reference', read_only=True)
    adaptation_details = UUIDSerializer(required=False, slug_field='reference', read_only=True)

    created = serializers.DateTimeField(read_only=True)
    modified = serializers.DateTimeField(read_only=True)
    created_by = serializers.CharField(read_only=True)
    provider = serializers.PrimaryKeyRelatedField(required=False, read_only=True)

    full_name = serializers.CharField(source='personal_details.full_name', read_only=True)
    eligibility_state = serializers.CharField(source='eligibility_check.state', read_only=True)
    diagnosis_state = serializers.CharField(source='diagnosis.state', read_only=True)
    postcode = serializers.CharField(source='personal_details.postcode', read_only=True)

    class Meta(CaseSerializerBase.Meta):
        fields = ()


class ExtendedUserSerializerBase(serializers.ModelSerializer):
    username = serializers.CharField(read_only=True, source='user.username')
    first_name = serializers.CharField(read_only=True,
                                       source='user.first_name')
    last_name = serializers.CharField(read_only=True, source='user.last_name')
    email = serializers.CharField(read_only=True, source='user.email')

    class Meta:
        fields = ()
