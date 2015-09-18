# -*- coding: utf-8 -*-
from django.core import validators
from django.db import models


class MoneyField(models.BigIntegerField):
    """
    Stores money to nearest penny as integer. e.g. £10.22 would be 1022
    """
    def __init__(self, max_value=9999999999, min_value=0, *args, **kwargs):
        self.max_value, self.min_value = max_value, min_value
        # kwargs['coerce'] = kwargs.pop('coerce', int)
        # kwargs['widget'] = forms.NumberInput

        super(MoneyField, self).__init__(*args, **kwargs)

        if max_value is not None:
            self.validators.append(validators.MaxValueValidator(max_value))
        if min_value is not None:
            self.validators.append(validators.MinValueValidator(min_value))
