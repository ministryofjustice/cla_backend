from numbers import Number
from collections import Iterable
from dateutil import parser

from django import template
from django.template.defaultfilters import stringfilter

from cla_common.money_interval.models import MoneyInterval

register = template.Library()


@stringfilter
def unslug(name):
    return name.replace("_", " ").capitalize()


register.filter("unslug", unslug)


@register.filter(is_safe=True)
def in_pounds(value):
    if isinstance(value, Number):
        value = value / 100.0
        return u"{val:.2f}".format(val=value)
    return value


@register.filter()
def as_date(date_string):
    try:
        return parser.parse(date_string, dayfirst=True)
    except Exception:
        return None


@register.filter()
def field_from_name(form, name):
    if name in form.fields:
        return form[name]


@register.filter()
def any_true(value):
    if isinstance(value, Iterable):
        return any(value)
    else:
        return bool(value)


@register.filter()
def mi_as_monthly(data):
    if not data:
        return data

    mi = MoneyInterval.from_dict(data)
    return mi.as_monthly()
