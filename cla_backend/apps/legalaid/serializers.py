from cla_eventlog.models import Log
from core.validators import validate_first_of_month
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from historic.models import CaseArchived
from legalaid.utils.csvupload.validators import ProviderCSVValidator
from rest_framework import serializers

from core.drf.fields import ThreePartDateField
from core.serializers import UUIDSerializer, ClaModelSerializer, PartialUpdateExcludeReadonlySerializerMixin, JSONField

from cla_common.constants import DISREGARDS, MATTER_TYPE_LEVELS, SPECIFIC_BENEFITS
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
    category = serializers.SlugRelatedField(slug_field="code", queryset=Category.objects.all())
    provider = serializers.PrimaryKeyRelatedField(queryset=Provider.objects.all())

    def validate(self, attrs):
        # if this is for a patch rather than a post then an instance already exists
        if self.instance is not None:
            instance = self.instance
        else:
            instance = OutOfHoursRota(**attrs)
        instance.clean()
        return attrs

    class Meta(object):
        model = OutOfHoursRota


class FeedbackSerializerBase(serializers.ModelSerializer):
    created_by = serializers.CharField(source="created_by.user.username", read_only=True)
    case = serializers.SlugRelatedField(slug_field="reference", read_only=True)

    comment = serializers.CharField(max_length=5000, read_only=True)

    justified = serializers.BooleanField(read_only=True)
    resolved = serializers.BooleanField(read_only=True)
    provider = serializers.SerializerMethodField()

    def get_provider(self, obj):
        return obj.created_by.provider.name

    class Meta(object):
        model = Feedback
        fields = ()


class CSVUploadSerializerBase(serializers.ModelSerializer):

    rows = serializers.SerializerMethodField()
    provider = serializers.CharField(read_only=True, source="provider.name")
    created_by = serializers.CharField(read_only=True, source="created_by.user.username")
    body = JSONField()

    def get_rows(self, obj):
        return len(obj.body)

    def validate_month(self, value):
        validate_first_of_month(value)
        return value

    def validate_body(self, body):
        if len(body) == 0:
            raise serializers.ValidationError("No rows found.")
        ProviderCSVValidator(body).validate()

        return body

    class Meta(object):
        model = CSVUpload
        fields = ()


class PropertySerializerBase(ClaModelSerializer):
    class Meta(object):
        model = Property
        fields = ()


class TotalsModelSerializer(ClaModelSerializer):
    total_fields = set()
    total = serializers.SerializerMethodField()

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

    # from DRF 3.0 onwards, there is no allow_add_remove option
    # writable nested serialization must be handed explicitly
    def create(self, validated_data):
        personal_details_data = validated_data.pop("personal_details")
        personal_details = PersonalDetails.objects.create(**personal_details_data)
        third_party_details = ThirdPartyDetails.objects.create(personal_details=personal_details, **validated_data)
        return third_party_details

    def update(self, instance, validated_data):
        personal_details_data = validated_data.pop("personal_details")
        # Save the fields on the instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Save the updated fields on the personal details object
        personal_details = instance.personal_details
        for attr, value in personal_details_data.items():
            setattr(personal_details, attr, value)
        personal_details.save()

        return instance

    class Meta(object):
        model = ThirdPartyDetails
        fields = ()


class PersonSerializerBase(ClaModelSerializer):
    income = IncomeSerializerBase(required=False)
    savings = SavingsSerializerBase(required=False)
    deductions = DeductionsSerializerBase(required=False)

    def create(self, validated_data):
        income_data = validated_data.pop("income", None)
        savings_data = validated_data.pop("savings", None)
        deductions_data = validated_data.pop("deductions", None)
        # # create the person and then attach the nested values
        if income_data:
            validated_data["income"] = IncomeSerializerBase().create(income_data)
        if savings_data:
            validated_data["savings"] = SavingsSerializerBase().create(savings_data)
        if deductions_data:
            validated_data["deductions"] = DeductionsSerializerBase().create(deductions_data)
        instance = Person.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        # need to check they exist in validated_data and also in instance
        income_data = validated_data.pop("income", None)
        savings_data = validated_data.pop("savings", None)
        deductions_data = validated_data.pop("deductions", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Save any updated fields on "income"
        if income_data:
            if instance.income:
                instance.income = IncomeSerializerBase().update(instance.income, income_data)
            else:
                instance.income = IncomeSerializerBase().create(income_data)

        # Save any updated fields on "savings"
        if savings_data:
            if instance.savings:
                instance.savings = SavingsSerializerBase().update(instance.savings, savings_data)
            else:
                instance.savings = SavingsSerializerBase().create(savings_data)

        # Save any updated fields on "deductions"
        if deductions_data:
            if instance.deductions:
                instance.deductions = DeductionsSerializerBase().update(instance.deductions, deductions_data)
            else:
                instance.deductions = DeductionsSerializerBase().create(deductions_data)

        instance.save()

        return instance

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
    notes = serializers.CharField(max_length=5000, required=False, allow_blank=True)
    categories = EODDetailsCategorySerializerBase(many=True, required=False)

    class Meta(object):
        model = EODDetails
        fields = ()

    # from DRF 3.0 onwards, there is no allow_add_remove option
    # writable nested serialization must be handed explicitly
    def create(self, validated_data):
        eod_details_category_data = validated_data.pop("categories")
        eoddetails = EODDetails.objects.create(**validated_data)
        for category in eod_details_category_data:
            EODDetailsCategory.objects.create(eod_details=eoddetails, **category)
        return eoddetails

    def update(self, instance, validated_data):
        eod_details_category_data = validated_data.pop("categories")
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        for category in eod_details_category_data:
            EODDetailsCategory.objects.create(eod_details=instance, **category)
        return instance


class EligibilityCheckSerializerBase(ClaModelSerializer):
    property_set = PropertySerializerBase(many=True, required=False)
    you = PersonSerializerBase(required=False, allow_null=True)
    partner = PersonSerializerBase(required=False, allow_null=True)
    category = serializers.SlugRelatedField(
        slug_field="code", required=False, queryset=Category.objects.all(), allow_null=True
    )
    your_problem_notes = serializers.CharField(max_length=500, required=False, allow_blank=True)
    notes = serializers.CharField(max_length=5000, required=False, allow_blank=True)
    specific_benefits = JSONField(required=False, allow_null=True)
    disregards = JSONField(required=False, allow_null=True)
    # DRF 3.0 fails to determine that these fields are nullable when trying to map django model fields to DRF fields
    # So we are setting here explicitly so that DRF doesn't try guessing if it's nullable
    is_you_or_your_partner_over_60 = serializers.NullBooleanField(default=None)
    on_passported_benefits = serializers.NullBooleanField(default=None)
    has_passported_proceedings_letter = serializers.NullBooleanField(default=None)
    on_nass_benefits = serializers.NullBooleanField(default=None)
    has_partner = serializers.NullBooleanField(default=None)

    class Meta(object):
        model = EligibilityCheck
        fields = ()

    # from DRF 3.0 onwards, there is no allow_add_remove option
    # writable nested serialization must be handed explicitly
    # needd to deal with you, partner, disputed_savings, and partner
    def create(self, validated_data):
        property_set_data = validated_data.pop("property_set", None)
        you_data = validated_data.pop("you", None)
        partner_data = validated_data.pop("partner", None)
        disputed_savings_data = validated_data.pop("disputed_savings", None)

        eligibility_check = EligibilityCheck.objects.create(**validated_data)
        if property_set_data:
            for prop in property_set_data:
                Property.objects.create(eligibility_check=eligibility_check, **prop)

        if you_data:
            eligibility_check.you = self.update_or_create_person(getattr(eligibility_check, "you"), you_data)

        if partner_data:
            eligibility_check.partner = self.update_or_create_person(
                getattr(eligibility_check, "partner"), partner_data
            )

        if disputed_savings_data:
            eligibility_check.disputed_savings = SavingsSerializerBase().create(disputed_savings_data)

        eligibility_check.save()

        return eligibility_check

    def update(self, instance, validated_data):
        disputed_savings_data = validated_data.pop("disputed_savings", None)
        you_data = validated_data.pop("you", None)
        partner_data = validated_data.pop("partner", None)
        property_set_data = validated_data.pop("property_set", None)

        # update the base object
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        # Save any updated fields on "you"

        if you_data:
            instance.you = self.update_or_create_person(getattr(instance, "you"), you_data)

        # Save any updated fields on "partner"
        if partner_data:
            instance.partner = self.update_or_create_person(getattr(instance, "partner"), partner_data)

        # Save any updated fields on "disputed_savings"
        if disputed_savings_data:
            if instance.disputed_savings:
                instance.disputed_savings = PersonSerializerBase().update(
                    instance.disputed_savings, disputed_savings_data
                )
            else:
                instance.disputed_savings = PersonSerializerBase().create(disputed_savings_data)

        # Save any updated fields on "property" or create new ones
        # if they are not new and updated then they should be deleted
        if property_set_data:
            self.update_property_set_data(instance, property_set_data)

        instance.save()
        return instance

    def update_or_create_person(self, instance, person_data):
        if instance:
            person = PersonSerializerBase().update(instance, person_data)
        else:
            person = PersonSerializerBase().create(person_data)
        return person

    def update_property_set_data(self, instance, property_set_data):
        ids_to_keep = []
        # validating loses the id of the property set:
        for index, prop_data in enumerate(property_set_data):
            # have to decide if this is an update or a create
            property_instance = None
            initial_prop = self.initial_data["property_set"][index]
            if "id" in initial_prop:
                # checks to see if property exists and is attached to current eligibility_check
                property_instance = Property.objects.filter(
                    pk=initial_prop["id"], eligibility_check_id=instance.id
                ).first()
                if property_instance:
                    property_instance = PropertySerializerBase().update(property_instance, prop_data)
            if property_instance is None:
                #  this should be a creation - didn't find a property attached to this eligibility to update
                prop_data["eligibility_check"] = instance
                property_instance = PropertySerializerBase().create(prop_data)
            ids_to_keep.append(property_instance.pk)
        # now delete any property that wasn't included in the validated_data
        instance.property_set.exclude(id__in=ids_to_keep).delete()

    def validate_property_set(self, value):
        """
        Checks that only one main property is selected
        """
        # Must allow for cases where there is only a partial value and main not included
        main_props = [prop for prop in value if prop.get("main")]
        if len(main_props) > 1:
            raise serializers.ValidationError("Only one main property allowed")
        return value

    def validate_specific_benefits(self, value):
        data_benefits = value
        if data_benefits:
            extra_fields = set(data_benefits.keys()) - set(SPECIFIC_BENEFITS.CHOICES_DICT.keys())
            if extra_fields:
                raise serializers.ValidationError("Fields %s not recognised" % ", ".join(list(extra_fields)))

            # translate into safer bool values
            data_benefits = {k: bool(v) for k, v in data_benefits.items()}
        return data_benefits

    def validate_disregards(self, value):
        data_disregards = value
        if data_disregards:
            extra_fields = set(data_disregards.keys()) - set(DISREGARDS.CHOICES_DICT.keys())
            if extra_fields:
                raise serializers.ValidationError("Fields %s not recognised" % ", ".join(list(extra_fields)))

            # translate into safer bool values
            data_disregards = {k: bool(v) for k, v in data_disregards.items()}
        return data_disregards

    def __has_category_changed(self):
        if not self.instance or self.instance.category is None:
            return False
        category = self.validated_data.get("category")
        if not category:
            return False
        return self.instance.category.name != category.name

    def save(self, **kwargs):
        # need to check the category before saving the current instance
        has_category_changed = self.__has_category_changed()
        obj = super(EligibilityCheckSerializerBase, self).save(**kwargs)
        obj.update_state()
        if has_category_changed:
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
    notes = serializers.CharField(max_length=10000, required=False, allow_blank=True)
    provider_notes = serializers.CharField(max_length=5000, required=False)
    matter_type1 = serializers.SlugRelatedField(
        slug_field="code",
        required=False,
        queryset=MatterType.objects.filter(level=MATTER_TYPE_LEVELS.ONE),
        allow_null=True,
    )
    matter_type2 = serializers.SlugRelatedField(
        slug_field="code",
        required=False,
        queryset=MatterType.objects.filter(level=MATTER_TYPE_LEVELS.TWO),
        allow_null=True,
    )
    media_code = serializers.SlugRelatedField(slug_field="code", required=False, queryset=MediaCode.objects.all())
    outcome_code = serializers.CharField(max_length=50, required=False, allow_blank=True)
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
    flagged_with_eod = serializers.BooleanField(read_only=True)

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

    def validate_password(self, password):
        if len(password) < 10:
            raise serializers.ValidationError("Password must be at least 10 characters long.")
        return password

    def validate(self, attrs):
        if User.objects.filter(username=attrs["user"]["username"]).exists():
            raise serializers.ValidationError("An account with this username already exists.")

        return super(ExtendedUserSerializerBase, self).validate(attrs)

    def create(self, validated_data):
        user = self.create_and_update_user(validated_data)
        return self.Meta.model.objects.create(user=user, **validated_data)

    def create_and_update_user(self, validated_data):
        user_details = validated_data.pop("user", None)

        user = None
        if user_details:
            user = User()
            user.username = user_details["username"]
            user.first_name = user_details["first_name"]
            user.last_name = user_details["last_name"]
            user.email = user_details["email"]
            user.set_password(user_details["password"])
            user.save()
        return user

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
    type_notes = serializers.SerializerMethodField()

    def get_type_notes(self, obj):
        if obj.provider_notes is not None:
            return obj.provider_notes
        return obj.operator_notes

    class Meta(object):
        model = CaseNotesHistory
        fields = ()
