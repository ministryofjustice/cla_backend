from legalaid.models import Category, EligibilityCheck, Person, Property, \
    Income, Savings, Deductions, PersonalDetails
from rest_framework import serializers


class UUIDSerializer(serializers.SlugRelatedField):
    def to_native(self, obj):
        return unicode(getattr(obj, self.slug_field))
