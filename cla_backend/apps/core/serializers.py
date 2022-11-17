from django.db import models
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from rest_framework_extensions.serializers import PartialUpdateSerializerMixin

from core import fields
from legalaid.fields import MoneyField, MoneyFieldDRF
from cla_common.money_interval.fields import MoneyIntervalField
from core.drf.fields import MoneyIntervalDRFField
from django.db.models.fields import FieldDoesNotExist


class MoneyIntervalModelSerializerMixin(object):
    def __init__(self, *args, **kwargs):
        # add a model serializer which is used throughout this project
        self._field_mapping[MoneyIntervalField] = MoneyIntervalDRFField
        super(MoneyIntervalModelSerializerMixin, self).__init__(*args, **kwargs)


class MoneyFieldModelSerializerMixin(object):
    def __init__(self, *args, **kwargs):
        # add a model serializer which is used throughout this project
        self._field_mapping[MoneyField] = MoneyFieldDRF
        super(MoneyFieldModelSerializerMixin, self).__init__(*args, **kwargs)


class UUIDSerializer(serializers.SlugRelatedField):
    def to_representation(self, obj):
        return unicode(getattr(obj, self.slug_field))


class NullBooleanModelSerializerMixin(object):
    def __init__(self, *args, **kwargs):
        # add a model serializer which is used throughout this project
        self._field_mapping[models.NullBooleanField] = fields.NullBooleanField
        super(NullBooleanModelSerializerMixin, self).__init__(*args, **kwargs)


class JSONField(serializers.Field):
    def to_representation(self, obj):
        return obj

    def to_internal_value(self, data):
        return data


class ClaModelSerializer(
    MoneyIntervalModelSerializerMixin, NullBooleanModelSerializerMixin, MoneyFieldModelSerializerMixin, ModelSerializer
):
    def restore_instance_for_validation(self, serializer, attrs):
        data = {}
        serializer_fields = serializer.fields
        model = serializer.Meta.model
        for field_name, field in serializer_fields.items():
            if field_name not in attrs or not attrs[field_name]:
                continue
            try:
                model._meta.get_field(field_name, many_to_many=False)
            except FieldDoesNotExist:
                # Don't include many-to-many fields
                continue

            if isinstance(field, serializers.ModelSerializer):
                data[field_name] = self.restore_instance_for_validation(field, attrs[field_name])
            else:
                data[field_name] = attrs[field_name]
        return model(**data)

    def validate(self, attrs):
        instance = self.restore_instance_for_validation(self, attrs)
        try:
            instance.full_clean(exclude=self.get_validation_exclusions(instance))
        except DjangoValidationError as exc:
            raise ValidationError(exc.message_dict)
        return super(ClaModelSerializer, self).validate(attrs)

    def get_validation_exclusions(self, instance=None):
        """
        Return a list of field names to exclude from model validation.
        """
        opts = self.Meta.model._meta
        exclusions = [field.name for field in opts.fields + opts.many_to_many]

        for field_name, field in self.fields.items():
            field_name = field.source or field_name
            if (
                field_name in exclusions
                and not field.read_only
                and (field.required or hasattr(instance, field_name))
                and not isinstance(field, serializers.Serializer)
            ):
                exclusions.remove(field_name)
        return exclusions

    def create_writeable_nested_fields_one_to_many(self, validated_data):
        fields = getattr(self.Meta, "writable_nested_fields", [])
        for writable_nested_field in fields:
            save_to_instance = True
            field_name = writable_nested_field
            if type(writable_nested_field) in [list, tuple]:
                field_name, save_to_instance = writable_nested_field
            data = validated_data.pop(field_name, None)
            if not data:
                continue

            field = self.fields.fields.get(field_name, None)
            field_instance = field.create(data)
            if save_to_instance:
                validated_data[field_name] = field_instance

    def create_writeable_nested_fields_many_to_many(self, instance, m2m_data):
        for field_name, data in m2m_data.items():
            if not data:
                continue
            m2m_serializer = self.fields.fields.get(field_name, None)
            for reason in data:
                if instance.reasons_for_contacting:
                    instance.reasons_for_contacting = m2m_serializer.update(instance.reasons_for_contacting, reason)
                else:
                    instance.reasons_for_contacting = m2m_serializer.create(reason)
            instance.save

    def filter_validated_data_m2m(self, validated_data):
        # removes many to many data from validated_data and returns as dict
        fields = getattr(self.Meta, "writable_nested_fields_m2m", [])
        m2m_data = {}
        for field in fields:
            if field in validated_data:
                m2m_data[field] = validated_data.pop(field)
        return m2m_data

    def create(self, validated_data):
        self.create_writeable_nested_fields_one_to_many(validated_data)
        model = self.Meta.model
        # todo move m2m fields in here
        # m2m_validated_data = self.filter_validated_data_m2m(validated_data)
        instance = model.objects.create(**validated_data)
        # self.create_writeable_nested_fields_many_to_many(instance, m2m_validated_data)
        return instance


class PartialUpdateExcludeReadonlySerializerMixin(PartialUpdateSerializerMixin):
    def _get_fields_for_partial_update(self):
        update_fields = set(super(PartialUpdateExcludeReadonlySerializerMixin, self)._get_fields_for_partial_update())
        exclude_fields = set([update_field for update_field in update_fields if self.fields[update_field].read_only])
        return list(update_fields - exclude_fields)
