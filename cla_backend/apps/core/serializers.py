from django.db import models
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from rest_framework_extensions.serializers import PartialUpdateSerializerMixin
from rest_framework_extensions.serializers import get_fields_for_partial_update

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

    def create_writeable_nested_fields_one_to_one(self, validated_data):
        writable_nested_fields = getattr(self.Meta, "writable_nested_fields", [])
        for field_name in writable_nested_fields:
            if not (field_name in validated_data):
                continue
            field = self.fields.fields.get(field_name, None)
            if not field:
                continue
            is_many = getattr(field, "many", False)
            if not is_many:
                # only remove this field if it is one to many
                data = validated_data.pop(field_name, None)
                field_instance = field.create(data)
                validated_data[field_name] = field_instance

    def create_writeable_nested_fields_many_to_many(self, parent, m2m_data):
        parent_model = type(parent)
        for field_name, data in m2m_data.items():
            if not data:
                continue
            m2m_serializer = self.fields.fields.get(field_name, None)
            parent_model_field = getattr(parent_model, field_name, None)
            if not parent_model_field:
                continue
            model_field_name = parent_model_field.related.field.name

            for item in data:
                item[model_field_name] = parent
            m2m_serializer.create(data)

    def filter_validated_data_m2m(self, validated_data):
        # removes many to many data from validated_data and returns as dict
        writable_nested_fields = getattr(self.Meta, "writable_nested_fields", [])
        m2m_data = {}
        for field_name in writable_nested_fields:
            field = self.fields.fields.get(field_name, None)
            if not field:
                continue

            is_many = getattr(field, "many", False)
            if not is_many:
                continue

            if field_name in validated_data:
                m2m_data[field_name] = validated_data.pop(field_name)
        return m2m_data

    def create(self, validated_data):
        self.create_writeable_nested_fields_one_to_one(validated_data)
        model = self.Meta.model
        m2m_validated_data = self.filter_validated_data_m2m(validated_data)
        instance = model.objects.create(**validated_data)
        self.create_writeable_nested_fields_many_to_many(instance, m2m_validated_data)
        return instance

    def update(self, instance, validated_data):
        self.create_writeable_nested_fields_one_to_one(validated_data)
        m2m_validated_data = self.filter_validated_data_m2m(validated_data)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        self.create_writeable_nested_fields_many_to_many(instance, m2m_validated_data)
        return instance

        # eod_details_category_data = validated_data.pop("categories")
        # for attr, value in validated_data.items():
        #     setattr(instance, attr, value)
        # instance.save()
        # EODDetailsSerializerBase.create_categories(instance, eod_details_category_data)
        # return instance


class PartialUpdateExcludeReadonlySerializerMixin(PartialUpdateSerializerMixin):
    def update(self, instance, validated_attrs):
        for attr, value in validated_attrs.items():
            setattr(instance, attr, value)
        if self.partial and isinstance(instance, self.Meta.model):
            instance.save(
                update_fields=getattr(self, "_update_fields") or self._get_fields_for_partial_update(validated_attrs)
            )
        else:
            instance.save()
        return instance

    def _get_fields_for_partial_update(self, validated_attrs):
        init_data = self.get_initial()
        init_data.update(validated_attrs)
        return get_fields_for_partial_update(
            opts=self.Meta,
            # Add data coming from validated_attrs, this will be the same as self.get_initial() but
            # include fields that our code has added
            init_data=init_data,
            fields=self.fields.fields,
        )
