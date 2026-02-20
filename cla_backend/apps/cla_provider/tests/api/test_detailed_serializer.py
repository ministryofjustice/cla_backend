from django.test import TestCase
from cla_provider.serializers import (
    CaseSerializer,
    DetailedCaseSerializer,
    CaseListSerializer
)


class SerializerConfigurationTest(TestCase):
    def test_serializer_fields(self):
        """Test that the serializers have the correct fields"""

        case_serializer = CaseSerializer()
        case_fields = case_serializer.Meta.fields

        list_serializer = CaseListSerializer()
        list_fields = list_serializer.Meta.fields

        detailed_serializer = DetailedCaseSerializer()
        detailed_fields = detailed_serializer.Meta.fields

        # CaseSerializer
        self.assertNotIn('state', case_fields)
        self.assertIn('eligibility_check', case_fields)

        # CaseListSerializer
        self.assertNotIn('state', list_fields)
        self.assertNotIn('eligibility_check', list_fields)
        self.assertIn('safe_to_contact', list_fields)
        self.assertIn('phone_number', list_fields)

        # DetailedCaseSerializer
        self.assertIn('state', detailed_fields)
        self.assertNotIn('eligibility_check', detailed_fields)

        # Validate that the other fields don't exist in the wrong place
        self.assertNotIn("state", set(CaseSerializer.Meta.fields))
        self.assertIn("eligibility_check", set(CaseSerializer.Meta.fields))

        self.assertNotIn("state", set(CaseListSerializer.Meta.fields))
        self.assertNotIn("eligibility_check", set(CaseListSerializer.Meta.fields))
        self.assertIn("safe_to_contact", set(CaseListSerializer.Meta.fields))
        self.assertIn("phone_number", set(CaseListSerializer.Meta.fields))

        self.assertIn("state", set(DetailedCaseSerializer.Meta.fields))
        self.assertNotIn("eligibility_check", set(DetailedCaseSerializer.Meta.fields))
