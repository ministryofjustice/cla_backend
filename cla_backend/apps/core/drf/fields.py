import datetime
import json
from django.core.validators import EMPTY_VALUES
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _


class ThreePartDateField(serializers.WritableField):
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

    def from_native(self, value):  # noqa: C901
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

    def to_native(self, value):
        """
        Transform datetime.date object to json.
        """
        if value is None:
            return value

        if isinstance(value, datetime.date):
            value = {"year": str(value.year), "month": str(value.month), "day": str(value.day)}
        return value
