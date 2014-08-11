from legalaid.serializers import UUIDSerializer, \
    EligibilityCheckSerializerBase, PropertySerializerBase, \
    PersonalDetailsSerializerBase, CaseSerializerBase


class PropertySerializer(PropertySerializerBase):

    @property
    def errors(self):
        return super(PropertySerializer, self).errors


class EligibilityCheckSerializer(EligibilityCheckSerializerBase):
    property_set = PropertySerializer(allow_add_remove=True, many=True, required=False)
    # TODO: DRF doesn't validate, fields that aren't REQ'd = True
    # we need to figure out a way to deal with it

    # dependants_young = IntegerField(default=0)
    # dependants_old = IntegerField(default=0)

    class Meta(EligibilityCheckSerializerBase.Meta):
        fields = (
            'reference',
            'category',
            'your_problem_notes',
            'notes',
            'property_set',
            'you',
            'partner',
            'dependants_young',
            'dependants_old',
            'is_you_or_your_partner_over_60',
            'has_partner',
            'on_passported_benefits',
            'on_nass_benefits',
        )


class PersonalDetailsSerializer(PersonalDetailsSerializerBase):
    class Meta(PersonalDetailsSerializerBase.Meta):
        fields = (
            'title', 'full_name', 'postcode', 'street',
            'mobile_phone', 'home_phone', 'email'
        )


class CaseSerializer(CaseSerializerBase):
    eligibility_check = UUIDSerializer(slug_field='reference')
    personal_details = PersonalDetailsSerializer()
    class Meta(CaseSerializerBase.Meta):
        fields = (
            'eligibility_check', 'personal_details', 'reference',
        )
