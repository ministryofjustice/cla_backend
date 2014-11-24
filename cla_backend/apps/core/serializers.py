from django.db import models

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from rest_framework_extensions.serializers import PartialUpdateSerializerMixin

from core import fields

from cla_common.money_interval.serializers import \
    MoneyIntervalModelSerializerMixin


class UUIDSerializer(serializers.SlugRelatedField):
    def to_native(self, obj):
        return unicode(getattr(obj, self.slug_field))


class NullBooleanModelSerializerMixin(object):
    def __init__(self, *args, **kwargs):
        # add a model serializer which is used throughout this project
        self.field_mapping = self.field_mapping.copy()
        self.field_mapping[models.NullBooleanField] = fields.NullBooleanField
        super(NullBooleanModelSerializerMixin, self).__init__(*args, **kwargs)


class JSONField(serializers.WritableField):

    def to_native(self, obj):
        return obj


class ClaModelSerializer(MoneyIntervalModelSerializerMixin,
                         NullBooleanModelSerializerMixin, ModelSerializer):
    pass


class PartialUpdateExcludeReadonlySerializerMixin(PartialUpdateSerializerMixin):
    def _get_fields_for_partial_update(self):
        update_fields = set(super(PartialUpdateExcludeReadonlySerializerMixin, self)._get_fields_for_partial_update())
        exclude_fields = set([update_field for update_field in update_fields if self.fields[update_field].read_only])
        return list(update_fields - exclude_fields)
