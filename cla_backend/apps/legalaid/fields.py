# -*- coding: utf-8 -*-
from django.core import validators
from django.db import models

from south.modelsinspector import add_introspection_rules

class MoneyField(models.BigIntegerField):
    """
    Stores money to nearest penny as integer. e.g. £10.22 would be 1022
    """
    def __init__(self, max_value=None, min_value=None, *args, **kwargs):
        self.max_value, self.min_value = max_value, min_value
        #kwargs['coerce'] = kwargs.pop('coerce', int)
        #kwargs['widget'] = forms.NumberInput

        super(MoneyField, self).__init__(*args, **kwargs)

        if max_value is not None:
            self.validators.append(validators.MaxValueValidator(max_value))
        if min_value is not None:
            self.validators.append(validators.MinValueValidator(min_value))

add_introspection_rules([
    (
        [MoneyField], # Class(es) these apply to
        [],         # Positional arguments (not used)
        {           # Keyword argument
            "min_value": ["min_value", {"default": None}],
            "max_value": ["max_value", {"default": None}],
        },
    ),
], ["^legalaid\.fields\.MoneyField"])
