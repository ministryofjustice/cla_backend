# -*- coding: utf-8 -*-
from rest_framework import serializers

from cla_eventlog.models import ComplaintLog
from cla_eventlog.serializers import LogSerializerBase
from core.fields import NullBooleanField
from core.serializers import UUIDSerializer
from .models import Category, Complaint


class CreatedByField(serializers.RelatedField):
    def to_native(self, obj):
        return {
            'username': obj.username,
            'first_name': obj.first_name,
            'last_name': obj.last_name,
        }


class CategorySerializerBase(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')


class ComplaintSerializerBase(serializers.ModelSerializer):
    eod = UUIDSerializer(slug_field='reference')
    owner = serializers.SlugRelatedField(slug_field='username', required=False)
    created_by = CreatedByField(read_only=True)
    category_name = serializers.CharField(
        source='category.name',
        read_only=True)
    full_name = serializers.CharField(
        source='eod.case.personal_details.full_name',
        read_only=True)
    category_of_law = serializers.CharField(
        source='eod.case.eligibility_check.category',
        read_only=True)
    case_reference = serializers.CharField(
        source='eod.case.reference',
        read_only=True)

    # # virtual fields created by extra SQL
    closed = serializers.DateTimeField(source='closed', read_only=True)
    voided = serializers.DateTimeField(source='voided', read_only=True)
    holding_letter = serializers.DateTimeField(
        source='holding_letter',
        read_only=True)
    full_letter = serializers.DateTimeField(
        source='full_letter',
        read_only=True)
    out_of_sla = NullBooleanField(source='out_of_sla', read_only=True)
    holding_letter_out_of_sla = NullBooleanField(
        source='holding_letter_out_of_sla',
        read_only=True)

    # # virtual fields on model
    status_label = serializers.CharField(
        source='status_label',
        read_only=True)
    requires_action_at = serializers.DateTimeField(
        source='requires_action_at',
        read_only=True)

    class Meta:
        model = Complaint
        read_only_fields = (
            'created', 'modified', 'resolved',
        )


class ComplaintLogSerializerBase(LogSerializerBase):
    class Meta:
        model = ComplaintLog
