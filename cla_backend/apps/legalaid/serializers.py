from cla_eventlog.models import Log
from core.validators import validate_first_of_month
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from historic.models import CaseArchived
from legalaid.utils.csvupload.validators import ProviderCSVValidator
from rest_framework import serializers

from core.drf.fields import ThreePartDateField
from core.serializers import UUIDSerializer, ClaModelSerializer, PartialUpdateExcludeReadonlySerializerMixin, JSONField

from cla_common.constants import MATTER_TYPE_LEVELS, SPECIFIC_BENEFITS
from cla_common.money_interval.models import MoneyInterval

from cla_provider.models import Provider, OutOfHoursRota, Feedback, CSVUpload
from cla_eventlog import registry as event_registry

from .models import (
    Category,
    Property,
    EligibilityCheck,
    Income,
    Savings,
    Deductions,
    Person,
    PersonalDetails,
    Case,
    ThirdPartyDetails,
    AdaptationDetails,
    MatterType,
    MediaCode,
    CaseNotesHistory,
    EODDetails,
    EODDetailsCategory,
    ContactResearchMethod,
)


class CategorySerializerBase(serializers.HyperlinkedModelSerializer):
    class Meta(object):
        model = Category
        fields = ("code", "name", "description", "ecf_available", "mandatory")


class ProviderSerializerBase(serializers.HyperlinkedModelSerializer):
    class Meta(object):
        model = Provider


class OutOfHoursRotaSerializerBase(ClaModelSerializer):
    category = serializers.SlugRelatedField(slug_field="code")
    provider = serializers.PrimaryKeyRelatedField()

    class Meta(object):
        model = OutOfHoursRota


class FeedbackSerializerBase(serializers.ModelSerializer):
    created_by = serializers.CharField(source="created_by.user.username", read_only=True)
    case = serializers.SlugRelatedField(slug_field="reference", read_only=True)

    comment = serializers.CharField(max_length=5000, read_only=True)

    justified = serializers.BooleanField(read_only=True)
    resolved = serializers.BooleanField(read_only=True)
    provider = serializers.SerializerMethodField("get_provider")

    def get_provider(self, obj):
        return obj.created_by.provider

    class Meta(object):
        model = Feedback
        fields = ()


class CSVUploadSerializerBase(serializers.ModelSerializer):

    rows = serializers.SerializerMethodField("get_rows")
    provider = serializers.CharField(read_only=True, source="provider.name")
    created_by = serializers.CharField(read_only=True, source="created_by.user.username")
    body = JSONField()

    def get_rows(self, obj):
        return len(obj.body)

    def validate_month(self, attrs, source):
        value = attrs[source]
        validate_first_of_month(value)
        return attrs

    def validate_body(self, attrs, source):
        value = attrs[source]
        if len(value) == 0:
            raise serializers.ValidationError("No rows found.")
        ProviderCSVValidator(value).validate()

        return attrs

    class Meta(object):
        model = CSVUpload
        fields = ()


class PropertySerializerBase(ClaModelSerializer):
    class Meta(object):
        model = Property
        fields = ()


class TotalsModelSerializer(ClaModelSerializer):
    total_fields = set()
    total = serializers.SerializerMethodField("get_total")

    def get_total(self, obj):
        total = 0
        for f in self.total_fields:
            value = getattr(obj, f, 0)

            if isinstance(value, MoneyInterval):
                subtotal = value.as_monthly()
            else:
                subtotal = getattr(obj, f, 0)

            if subtotal is not None:
                total += subtotal
        return total


class IncomeSerializerBase(TotalsModelSerializer):
    total_fields = {
        "earnings",
        "self_employment_drawings",
        "benefits",
        "tax_credits",
        "child_benefits",
        "maintenance_received",
        "pension",
        "other_income",
    }

    class Meta(object):
        model = Income
        fields = ()


class SavingsSerializerBase(TotalsModelSerializer):
    total_fields = {"bank_balance", "investment_balance", "asset_balance", "credit_balance"}

    class Meta(object):
        model = Savings
        fields = ()


class DeductionsSerializerBase(TotalsModelSerializer):
    total_fields = {
        "criminal_legalaid_contributions",
        "income_tax",
        "national_insurance",
        "maintenance",
        "childcare",
        "mortgage",
        "rent",
    }

    class Meta(object):
        model = Deductions
        fields = ()


class PersonalDetailsSerializerBase(serializers.ModelSerializer):
    class Meta(object):
        model = PersonalDetails
        fields = ()


class PersonalDetailsSerializerFull(PersonalDetailsSerializerBase):
    dob = ThreePartDateField(required=False, source="date_of_birth")
    has_diversity = serializers.SerializerMethodField("diversity_bool")

    def diversity_bool(self, obj):
        return bool(obj.diversity)

    class Meta(PersonalDetailsSerializerBase.Meta):
        fields = ()


class ThirdPartyPersonalDetailsSerializerBase(PersonalDetailsSerializerBase):
    class Meta(PersonalDetailsSerializerBase.Meta):
        fields = ()


class ThirdPartyDetailsSerializerBase(serializers.ModelSerializer):
    personal_details = ThirdPartyPersonalDetailsSerializerBase(required=True)

    class Meta(object):
        model = ThirdPartyDetails
        fields = ()


class PersonSerializerBase(ClaModelSerializer):
    income = IncomeSerializerBase(required=False)
    savings = SavingsSerializerBase(required=False)
    deductions = DeductionsSerializerBase(required=False)

    class Meta(object):
        model = Person
        fields = ()


class AdaptationDetailsSerializerBase(serializers.ModelSerializer):
    bsl_webcam = serializers.BooleanField(label="BSL - Webcam", required=False)
    minicom = serializers.BooleanField(label="Minicom", required=False)
    text_relay = serializers.BooleanField(label="Text relay", required=False)
    skype_webcam = serializers.BooleanField(label="Skype", required=False)
    callback_preference = serializers.BooleanField(label="Callback preference", required=False)
    no_adaptations_required = serializers.BooleanField(label="No adaptations required", required=False)

    class Meta(object):
        model = AdaptationDetails
        fields = ()


class EODDetailsCategorySerializerBase(serializers.ModelSerializer):
    class Meta(object):
        model = EODDetailsCategory
        fields = ("category", "is_major")


class EODDetailsSerializerBase(serializers.ModelSerializer):
    notes = serializers.CharField(max_length=5000, required=False)
    categories = EODDetailsCategorySerializerBase(many=True, allow_add_remove=True, required=False)

    class Meta(object):
        model = EODDetails
        fields = ()


class EligibilityCheckSerializerBase(ClaModelSerializer):
    property_set = PropertySerializerBase(allow_add_remove=True, many=True, required=False)
    you = PersonSerializerBase(required=False)
    partner = PersonSerializerBase(required=False)
    category = serializers.SlugRelatedField(slug_field="code", required=False)
    your_problem_notes = serializers.CharField(max_length=500, required=False)
    notes = serializers.CharField(max_length=5000, required=False)
    specific_benefits = JSONField(required=False)

    class Meta(object):
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

    def validate_specific_benefits(self, attrs, source):
        if source in attrs:
            data_benefits = attrs[source]
            if data_benefits:
                extra_fields = set(data_benefits.keys()) - set(SPECIFIC_BENEFITS.CHOICES_DICT.keys())
                if extra_fields:
                    raise serializers.ValidationError("Fields %s not recognised" % ", ".join(list(extra_fields)))

                # translate into safer bool values
                data_benefits = {k: bool(v) for k, v in data_benefits.items()}
                attrs[source] = data_benefits

        return attrs

    def save(self, **kwargs):
        obj = super(EligibilityCheckSerializerBase, self).save(**kwargs)
        obj.update_state()
        diff = obj.diff
        if "category" in diff:
            # if the category has been updated then reset mattertype on
            # corresponding case
            obj.reset_matter_types()
        return obj


class MatterTypeSerializerBase(ClaModelSerializer):
    category = serializers.SlugRelatedField(slug_field="code", read_only=True)

    class Meta(object):
        model = MatterType
        fields = ("category", "code", "description", "level")


class MediaCodeSerializerBase(ClaModelSerializer):
    group = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta(object):
        model = MediaCode
        fields = ("group", "name", "code")


class ContactResearchMethodSerializerBase(ClaModelSerializer):
    group = serializers.SlugRelatedField(slug_field="method", read_only=True)

    class Meta(object):
        model = ContactResearchMethod
        fields = ("method", "id")


class CaseSerializerBase(PartialUpdateExcludeReadonlySerializerMixin, ClaModelSerializer):
    eligibility_check = UUIDSerializer(slug_field="reference", read_only=True)
    diagnosis = UUIDSerializer(slug_field="reference", required=False, read_only=True)
    personal_details = PersonalDetailsSerializerBase()
    notes = serializers.CharField(max_length=10000, required=False)
    provider_notes = serializers.CharField(max_length=5000, required=False)
    matter_type1 = serializers.SlugRelatedField(
        slug_field="code", required=False, queryset=MatterType.objects.filter(level=MATTER_TYPE_LEVELS.ONE)
    )
    matter_type2 = serializers.SlugRelatedField(
        slug_field="code", required=False, queryset=MatterType.objects.filter(level=MATTER_TYPE_LEVELS.TWO)
    )
    media_code = serializers.SlugRelatedField(slug_field="code", required=False)
    outcome_code = serializers.CharField(max_length=50, required=False)
    outcome_description = serializers.SerializerMethodField("_get_outcome_description")
    call_started = serializers.SerializerMethodField("_call_started")

    def _call_started(self, case):
        return Log.objects.filter(case=case, code="CALL_STARTED").exists()

    def _get_outcome_description(self, case):
        return event_registry.event_registry.all().get(case.outcome_code, {}).get("description", "")

    def _get_fields_for_partial_update(self):
        fields = super(CaseSerializerBase, self)._get_fields_for_partial_update()
        fields.append("modified")
        return fields

    def validate(self, attrs):
        attrs = super(CaseSerializerBase, self).validate(attrs)
        if attrs.get("exempt_user") and not attrs.get("exempt_user_reason"):
            raise ValidationError({u"exempt_user_reason": [u"A reason is required if client is exempt."]})
        return attrs

    class Meta(object):
        model = Case
        fields = ()
        exclude = ("audit_log",)
        read_only_fields = ("exempt_user", "exempt_user_reason")


class CaseSerializerFull(CaseSerializerBase):
    eligibility_check = UUIDSerializer(slug_field="reference", required=False, read_only=True)

    full_name = serializers.CharField(source="personal_details.full_name", read_only=True)
    postcode = serializers.CharField(source="personal_details.postcode", read_only=True)
    case_count = serializers.IntegerField(source="personal_details.case_count", read_only=True)

    personal_details = UUIDSerializer(required=False, slug_field="reference", read_only=True)
    thirdparty_details = UUIDSerializer(required=False, slug_field="reference", read_only=True)
    adaptation_details = UUIDSerializer(required=False, slug_field="reference", read_only=True)

    eod_details = UUIDSerializer(required=False, slug_field="reference", read_only=True)
    flagged_with_eod = serializers.BooleanField(source="flagged_with_eod", read_only=True)

    created = serializers.DateTimeField(read_only=True)
    modified = serializers.DateTimeField(read_only=True)
    created_by = serializers.CharField(read_only=True)
    provider = serializers.PrimaryKeyRelatedField(required=False, read_only=True)
    provider_viewed = serializers.DateTimeField(required=False, read_only=True)

    eligibility_state = serializers.CharField(source="eligibility_check.state", read_only=True)
    diagnosis_state = serializers.CharField(source="diagnosis.state", read_only=True)

    date_of_birth = serializers.CharField(source="personal_details.date_of_birth", read_only=True)
    category = serializers.CharField(source="diagnosis.category.name", read_only=True)

    class Meta(CaseSerializerBase.Meta):
        fields = ()


class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = User
        fields = ("id", "username", "email", "first_name", "last_name")


class ExtendedUserSerializerBase(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username")
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    email = serializers.CharField(source="user.email")
    password = serializers.CharField(source="user.password", write_only=True)
    last_login = serializers.DateTimeField(source="user.last_login", read_only=True)
    created = serializers.DateTimeField(source="user.date_joined", read_only=True)
    user = UserSerializer()

    def validate_password(self, attrs, source):
        if len(attrs[source]) < 10:
            raise serializers.ValidationError("Password must be at least 10 characters long.")
        return attrs

    def validate(self, attrs):
        if User.objects.filter(username=attrs["user.username"]).exists():
            raise serializers.ValidationError("An account with this username already exists.")

        return super(ExtendedUserSerializerBase, self).validate(attrs)

    def restore_object(self, attrs, instance=None):
        restored = super(ExtendedUserSerializerBase, self).restore_object(attrs, instance=instance)
        user = User()
        user.username = attrs["user.username"]
        user.first_name = attrs["user.first_name"]
        user.last_name = attrs["user.last_name"]
        user.email = attrs["user.email"]
        user.set_password(attrs["user.password"])
        user.save()
        restored.user = user
        return restored

    class Meta(object):
        fields = ()


class CaseArchivedSerializerBase(serializers.ModelSerializer):
    date_of_birth = ThreePartDateField(required=False)
    date_specialist_referred = ThreePartDateField(required=False)
    date_specialist_closed = ThreePartDateField(required=False)

    class Meta(object):
        model = CaseArchived
        fields = ()


class CaseNotesHistorySerializerBase(ClaModelSerializer):
    created_by = serializers.CharField(read_only=True, source="created_by.username")
    created = serializers.DateTimeField(read_only=True)
    operator_notes = serializers.CharField(read_only=True)
    provider_notes = serializers.CharField(read_only=True)
    type_notes = serializers.SerializerMethodField("get_type_notes")

    def get_type_notes(self, obj):
        if obj.provider_notes is not None:
            return obj.provider_notes
        return obj.operator_notes

    class Meta(object):
        model = CaseNotesHistory
        fields = ()
