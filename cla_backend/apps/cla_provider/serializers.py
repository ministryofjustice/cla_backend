from cla_eventlog.serializers import LogSerializerBase
from rest_framework import serializers

from legalaid.serializers import UUIDSerializer, \
    EligibilityCheckSerializerBase, \
    PropertySerializerBase, SavingsSerializerBase, \
    PersonSerializerBase, PersonalDetailsSerializerBase, \
    CaseSerializerBase, CategorySerializerBase,  \
    ProviderSerializerBase, \
    ExtendedUserSerializerBase, \
    AdaptationDetailsSerializerBase

from .models import Staff


class EligibilityCheckSerializer(EligibilityCheckSerializerBase):
    notes = serializers.CharField(max_length=500, required=False, read_only=True)
    disputed_savings = SavingsSerializerBase(required=False)

    class Meta(EligibilityCheckSerializerBase.Meta):
        fields = (
            'reference',
            'category',
            'your_problem_notes',
            'notes',
            'property_set',
            'you',
            'partner',
            'disputed_savings',
            'dependants_young',
            'dependants_old',
            'is_you_or_your_partner_over_60',
            'has_partner',
            'on_passported_benefits',
            'on_nass_benefits',
            'state'
        )


class PersonalDetailsSerializer(PersonalDetailsSerializerBase):
    class Meta(PersonalDetailsSerializerBase.Meta):
        fields = (
            'title', 'full_name', 'postcode', 'street',
            'mobile_phone', 'home_phone'
        )


class LogSerializer(LogSerializerBase):

    class Meta(LogSerializerBase.Meta):
        fields = ('code',
                  'created_by',
                  'created',
                  'notes',
                  'level',
                  'type'
        )


class CaseSerializer(CaseSerializerBase):
    LOG_SERIALIZER = LogSerializer

    eligibility_check = UUIDSerializer(slug_field='reference', required=False, read_only=True)

    personal_details = UUIDSerializer(required=False, slug_field='reference', read_only=True)
    thirdparty_details = UUIDSerializer(required=False, slug_field='reference', read_only=True)
    adaptation_details = UUIDSerializer(required=False, slug_field='reference', read_only=True)

    created = serializers.DateTimeField(read_only=True)
    modified = serializers.DateTimeField(read_only=True)
    created_by = serializers.CharField(read_only=True)
    provider = serializers.PrimaryKeyRelatedField(required=False)
    locked_by = serializers.CharField(read_only=True)
    locked_at = serializers.DateTimeField(read_only=True)

    full_name = serializers.CharField(source='personal_details.full_name', read_only=True)
    eligibility_state = serializers.CharField(source='eligibility_check.state', read_only=True)
    diagnosis_state = serializers.CharField(source='diagnosis.state', read_only=True)
    postcode = serializers.CharField(source='personal_details.postcode', read_only=True)


    class Meta(CaseSerializerBase.Meta):
        fields = (
            'eligibility_check', 'personal_details',
            'reference', 'created', 'modified', 'created_by',
            'provider', 'log_set', 'locked_by', 'locked_at',
            'notes', 'provider_notes', 'laa_reference',
            'requires_action_by',
            'thirdparty_details',
            'eligibility_state',
            'adaptation_details',
            'matter_type1',
            'matter_type2',
            'full_name',
            'postcode',
            'diagnosis_state',
            'diagnosis',
        )

class AdaptationDetailsSerializer(AdaptationDetailsSerializerBase):
    class Meta(AdaptationDetailsSerializerBase.Meta):
        fields = (
            'bsl_webcam', 'minicom', 'text_relay', 'skype_webcam',
            'language', 'notes', 'reference', 'callback_preference'
        )

class ProviderSerializer(ProviderSerializerBase):
    class Meta(ProviderSerializerBase.Meta):
        fields = ('name', 'id')


class StaffSerializer(ExtendedUserSerializerBase):
    provider = ProviderSerializer(read_only=True)

    class Meta:
        model = Staff
        fields = (
            'username', 'first_name', 'last_name', 'email', 'provider',
            'is_manager'
        )
