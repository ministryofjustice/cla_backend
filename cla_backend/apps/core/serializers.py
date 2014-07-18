from cla_common.money_interval.serializers import \
    MoneyIntervalModelSerializerMixin
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from django.db import models
from core import fields


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
