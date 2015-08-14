# -*- coding: utf-8 -*-
from rest_framework import serializers
from legalaid.serializers import EODDetailsSerializerBase, CaseSerializerBase

from .models import Category, Complaint


class ComplaintEodSerializer(EODDetailsSerializerBase):
    class Meta(EODDetailsSerializerBase.Meta):
        fields = (
            'reference',
            'notes',
            'categories',
        )


class ComplaintCaseSerializer(CaseSerializerBase):
    class Meta(CaseSerializerBase.Meta):
        fields = (
        )


class CategorySerializerBase(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')


class ComplaintSerializerBase(serializers.ModelSerializer):
    category = CategorySerializerBase()
    eod = ComplaintEodSerializer()
    case = ComplaintCaseSerializer()

    class Meta:
        model = Complaint
