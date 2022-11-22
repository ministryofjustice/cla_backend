# coding=utf-8
from django.core import validators
from django.db import models
from rest_framework.serializers import Field


class MoneyFieldDRF(Field):
    def __init__(self, max_value=9999999999, min_value=0, *args, **kwargs):
        kwargs.setdefault("validators", [])
        if max_value is not None:
            kwargs["validators"].append(validators.MaxValueValidator(max_value))
        if min_value is not None:
            kwargs["validators"].append(validators.MinValueValidator(min_value))
        super(MoneyFieldDRF, self).__init__(*args, **kwargs)

    def to_representation(self, obj):
        return obj

    def to_internal_value(self, data):
        return data


class MoneyField(models.BigIntegerField):
    """
    Stores money to nearest penny as integer. e.g. £10.22 would be 1022
    """

    def __init__(self, max_value=9999999999, min_value=0, *args, **kwargs):
        # add our validators first because DRF 3.0 only accepts the first validator
        # see line 152 in rest_framework.utils.field_mapping.get_field_kwargs
        kwargs.setdefault("validators", [])
        if max_value is not None:
            max_validator = validators.MaxValueValidator(max_value)
            if max_validator not in kwargs["validators"]:
                kwargs["validators"].append(max_validator)
        if min_value is not None:
            min_validator = validators.MinValueValidator(min_value)
            if min_validator not in kwargs["validators"]:
                kwargs["validators"].append(min_validator)
        super(MoneyField, self).__init__(*args, **kwargs)
