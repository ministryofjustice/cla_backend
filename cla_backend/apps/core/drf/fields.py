import datetime
import json
from django.core.validators import EMPTY_VALUES
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from django.core import validators
from cla_common.money_interval.models import MoneyInterval
from cla_common.money_interval.fields import MoneyIntervalField


class MoneyIntervalFieldMaxValidator(validators.MaxValueValidator):
    def __call__(self, obj):
        value = getattr(obj, "per_interval_value", None)
        if value is not None:
            return super(MoneyIntervalFieldMaxValidator, self).__call__(value)


class MoneyIntervalFieldMinValidator(validators.MinValueValidator):
    def __call__(self, obj):
        value = getattr(obj, "per_interval_value", None)
        if value is not None:
            return super(MoneyIntervalFieldMinValidator, self).__call__(value)


class MoneyIntervalDRFField(serializers.Field):
    type_name = "MoneyIntervalDRFField"
    type_label = "moneyIntervalDRFField"
    form_field_class = MoneyIntervalField

    def __init__(self, max_value=9999999999, min_value=0, *args, **kwargs):
        kwargs.setdefault("validators", [])
        if max_value is not None:
            kwargs["validators"].append(MoneyIntervalFieldMaxValidator(max_value))
        if min_value is not None:
            kwargs["validators"].append(MoneyIntervalFieldMinValidator(min_value))
        super(MoneyIntervalDRFField, self).__init__(*args, **kwargs)

    def to_representation(self, value):
        # TODO remove comment  - must always be implemented, this was in field_to_native
        if not value:
            return None

        return {"interval_period": value.interval_period, "per_interval_value": value.per_interval_value}

    def to_internal_value(self, value):
        # TODO remove comment - from_native is replaced by to_internal_value DRF 3.0
        if not value:
            return None

        if isinstance(value, dict):
            interval_period, per_interval_value = value.get("interval_period"), value.get("per_interval_value")
            if not (interval_period and per_interval_value != None):  # noqa E711
                return None

            mi = MoneyInterval(interval_period, pennies=per_interval_value or 0)
        else:
            # TODO - remove - only here for mock test - temporary
            mi = MoneyInterval("per_month", pennies=value)
        return mi


class ThreePartDateField(serializers.Field):
    """
    A serializer field for handling three part date time JSON formatted
    datetime.date.

    Expected input format:
        {
            "day": 25,
            "month": 12,
            "year": 2012
        }
    """

    type_name = "ThreePartDateField"
    type_label = "date"

    default_error_messages = {
        "invalid":
        # Translators: '{ "day": 25, "month": 12, "year": 2012 }' should be left in as-is
        _('Date field has wrong format. Use { "day": 25, "month": 12, "year": 2012 }')
    }

    def to_internal_value(self, value):  # noqa: C901
        """
        Parse json data and return a date object
        """
        if value in EMPTY_VALUES:
            return None

        if type(value) in [str, unicode]:
            try:
                value = value.replace("'", '"')
                value = json.loads(value)
            except ValueError:
                msg = self.error_messages["invalid"]
                raise serializers.ValidationError(msg)
        if value:
            day = value.get("day")
            month = value.get("month")
            year = value.get("year")

            date_components = all([day, month, year])
            if date_components:
                try:
                    dt_object = datetime.date(int(year), int(month), int(day))
                except ValueError as ve:
                    raise serializers.ValidationError(ve)

                if int(year) < 1900:
                    raise serializers.ValidationError("year must be >= 1900")
                return dt_object
            elif not date_components:
                return None
            msg = self.error_messages["invalid"]
            raise serializers.ValidationError(msg)

    def to_representation(self, value):
        """
        Transform datetime.date object to json.
        """
        if value is None:
            return value

        if isinstance(value, datetime.date):
            value = {"year": str(value.year), "month": str(value.month), "day": str(value.day)}
        return value
