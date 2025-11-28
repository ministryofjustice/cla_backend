#!/usr/bin/env python
"""
Test script to verify the detailed case serializer configuration
"""
import json

def test_serializer_fields():
    """Test that the serializers have the correct fields"""

    # Import the serializers
    import sys
    import os
    sys.path.insert(0, '/Users/imtiaz.ahmed/Documents/GitHub/cla_backend-master')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cla_backend.settings.testing')

    try:
        import django
        django.setup()

        from cla_provider.serializers import CaseSerializer, DetailedCaseSerializer, CaseListSerializer

        # Test CaseSerializer fields
        case_serializer = CaseSerializer()
        case_fields = case_serializer.Meta.fields
        print("CaseSerializer fields:")
        print("  - Has 'state': {}".format('state' in case_fields))
        print("  - Has 'eligibility_check': {}".format('eligibility_check' in case_fields))
        print()

        # Test CaseListSerializer fields
        list_serializer = CaseListSerializer()
        list_fields = list_serializer.Meta.fields
        print("CaseListSerializer fields:")
        print("  - Has 'state': {}".format('state' in list_fields))
        print("  - Has 'eligibility_check': {}".format('eligibility_check' in list_fields))
        print("  - Has 'safe_to_contact': {}".format('safe_to_contact' in list_fields))
        print()

        # Test DetailedCaseSerializer fields
        detailed_serializer = DetailedCaseSerializer()
        detailed_fields = detailed_serializer.Meta.fields
        print("DetailedCaseSerializer fields:")
        print("  - Has 'state': {}".format('state' in detailed_fields))
        print("  - Has 'eligibility_check': {}".format('eligibility_check' in detailed_fields))
        print()

        # Test that state field is properly defined in DetailedCaseSerializer
        print("DetailedCaseSerializer field definitions:")
        print("  - 'state' field type: {}".format(type(detailed_serializer.fields.get('state', 'Not defined'))))
        print()

        # Verify expectations
        assert 'state' not in case_fields, "CaseSerializer should NOT have 'state' field"
        assert 'eligibility_check' in case_fields, "CaseSerializer should have 'eligibility_check' field"

        assert 'state' not in list_fields, "CaseListSerializer should NOT have 'state' field"
        assert 'eligibility_check' not in list_fields, "CaseListSerializer should NOT have 'eligibility_check' field"
        assert 'safe_to_contact' in list_fields, "CaseListSerializer should have 'safe_to_contact' field"

        assert 'state' in detailed_fields, "DetailedCaseSerializer should have 'state' field"
        assert 'eligibility_check' not in detailed_fields, "DetailedCaseSerializer should NOT have 'eligibility_check' field"

        print("[PASS] All tests passed!")
        print("The serializer configuration is correct:")
        print("  - 'state' field is only available in DetailedCaseSerializer")
        print("  - 'eligibility_check' field is removed from DetailedCaseSerializer")
        print("  - 'safe_to_contact' field is available in CaseListSerializer")

    except Exception as e:
        print("[ERROR] Error: {}".format(e))
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_serializer_fields()
