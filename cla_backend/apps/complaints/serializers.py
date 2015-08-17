# -*- coding: utf-8 -*-
from rest_framework import serializers

from .models import Category, Complaint


class CategorySerializerBase(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')


class ClaSerializerMethodField(serializers.SerializerMethodField):
    def field_to_native(self, obj, field_name):
        meth = getattr(self.parent, self.method_name)
        try:
            return self.to_native(meth(obj))
        except AttributeError:
            pass


class ComplaintSerializerBase(serializers.ModelSerializer):
    category = CategorySerializerBase()
    full_name = ClaSerializerMethodField('_get_full_name')
    category_of_law = ClaSerializerMethodField('_get_category_of_law')
    case_reference = ClaSerializerMethodField('_get_case_reference')

    class Meta:
        model = Complaint

    def _get_full_name(self, instance):
        return instance.eod.case.personal_details.full_name

    def _get_category_of_law(self, instance):
        return instance.eod.case.eligibility_check.category

    def _get_case_reference(self, instance):
        return instance.eod.case.reference
