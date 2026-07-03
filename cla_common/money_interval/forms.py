from django import forms
from django.forms import widgets

from .models import MoneyInterval


class MoneyIntervalWidget(widgets.MultiWidget):
    def __init__(self, attrs=None):
        if not attrs:
            attrs = {}

        new_class = attrs.get("class", "") + " InlineField"
        select_attrs = {"class": new_class.strip()}
        select_attrs.update(attrs)

        intervals = MoneyInterval.get_intervals_for_widget()

        _widgets = (widgets.NumberInput(attrs=attrs), widgets.Select(attrs=select_attrs, choices=intervals))
        super(MoneyIntervalWidget, self).__init__(_widgets, attrs)

    def decompress(self, value):
        if value and isinstance(value, dict):
            return [
                value["per_interval_value"] if "per_interval_value" in value else None,
                value["interval_period"] if "interval_period" in value else None,
            ]
        else:
            return [None, None]

    def format_output(self, rendered_widgets):

        # there should be a number input and a dropdown
        return u"".join(rendered_widgets)


class MoneyIntervalField(forms.MultiValueField):
    widget = MoneyIntervalWidget

    def __init__(self, max_value=2500000, min_value=0, step=None, *args, **kwargs):
        self.max_value, self.min_value, self.step = max_value, min_value, step or "0.01"

        if "initial" not in kwargs:
            kwargs["initial"] = {"interval_period": "per_month"}

        # intervals = MoneyInterval.get_intervals_for_widget()
        fields = [forms.DecimalField(max_value=max_value, min_value=min_value, decimal_places=2), forms.CharField()]

        super(MoneyIntervalField, self).__init__(fields, *args, **kwargs)

    #         if max_value is not None:
    #             self.validators.append(validators.MaxValueValidator(max_value))
    #         if min_value is not None:
    #             self.validators.append(validators.MinValueValidator(min_value))

    def compress(self, data_vals):
        if len(data_vals) == 2:
            # value = int(Decimal(data_vals[0]).quantize(ZERO_DP))*100
            # compressed = "%s-%s" % (value, data_vals[1])
            # return compressed
            mi = MoneyInterval(data_vals[1], pounds=data_vals[0])
            # a serialiser has been deemed too much
            return {
                "interval_period": mi.interval_period,
                "per_interval_value": mi.per_interval_value,
                "per_month": mi.as_monthly(),
            }
        return None

    def widget_attrs(self, widget):
        attrs = super(MoneyIntervalField, self).widget_attrs(widget)

        if isinstance(widget, MoneyIntervalWidget):
            if self.min_value is not None:
                widget.widgets[0].attrs["min"] = self.min_value
            if self.max_value is not None:
                widget.widgets[0].attrs["max"] = self.max_value
            if self.step is not None:
                widget.widgets[0].attrs["step"] = self.step

        return attrs
