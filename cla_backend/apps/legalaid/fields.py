# -*- coding: utf-8 -*-
from django.core import exceptions, validators
from django.db import models
from django.utils.translation import ugettext_lazy as _

from south.modelsinspector import add_introspection_rules

from cla_common.helpers import MoneyInterval

class MoneyField(models.BigIntegerField):
    """
    Stores money to nearest penny as integer. e.g. £10.22 would be 1022
    """
    def __init__(self, max_value=9999999999, min_value=0, *args, **kwargs):
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



_interval_period_field_name = lambda name: "%s_interval_period" % name
_per_interval_value_field_name = lambda name: "%s_per_interval_value" % name

class MoneyIntervalFieldCreator(object):
    """
    An equivalent to Django's default attribute descriptor class (enabled via
    the SubfieldBase metaclass, see module doc for details). However, instead
    of calling to_python() on our MoneyIntervalField class, it stores the three
    different parts of a money field - 'value' (default value, e.g. probably
    normalised to monthly figure) interval_period and per_interval_value - each
    is stored separately, and updates them whenever something is assigned. If 
    the attribute is read, it builds the MoneyIntervalField instance "on-demand"
    with the current data.
    """
    def __init__(self, field):
        self.field = field
        self.interval_period_field_name = _interval_period_field_name(self.field.name)
        self.per_interval_value_field_name = _per_interval_value_field_name(self.field.name)

    def __get__(self, obj, type=None):
        if obj is None:
            raise AttributeError('Can only be accessed via an instance.')

        value = obj.__dict__[self.field.name]
        if value is None: return None
        elif isinstance(value, dict):
            try:
                mi = MoneyInterval(interval_period=value['interval_period'])
                mi.set_as_pennies(value['per_interval_value'])
            except:
                pass
            return mi
        elif isinstance(value, MoneyInterval):
            return value
        elif hasattr(obj, self.interval_period_field_name) and hasattr(obj, self.per_interval_value_field_name):
            mi = MoneyInterval(interval_period=getattr(obj, self.interval_period_field_name))
            mi.set_as_pennies(getattr(obj, self.per_interval_value_field_name))
            return mi
        else:
            raise Exception("probably needs to instantiate from something else")

    def __set__(self, obj, value):

        #if isinstance(value, MoneyInterval): ???????????????
        if value.__class__.__name__ == "MoneyInterval":
            # MoneyInterval is assigned: take over it's values
            obj.__dict__[self.field.name] = value.as_monthly()
            setattr(obj, self.interval_period_field_name, value.interval_period)
            setattr(obj, self.per_interval_value_field_name, value.per_interval_value)
        else:
            # just the default 'value'
            obj.__dict__[self.field.name] = value



class MoneyIntervalField(models.BigIntegerField):
    """
    Stores money to nearest penny as integer. e.g. £10.22 would be 1022
    """
    
    """
    Multiple DB columns from one django model field.
    Inspiration from
    http://blog.elsdoerfer.name/2008/01/08/fuzzydates-or-one-django-model-field-multiple-database-columns/
    
    """
    default_error_messages = {
        'invalid': _("'%(value)s' value must be an MoneyInterval dictionary."),
    }
        
    def __init__(self, max_value=9999999999, min_value=0, *args, **kwargs):
        self.max_value, self.min_value = max_value, min_value
        #kwargs['coerce'] = kwargs.pop('coerce', int)
        #kwargs['widget'] = forms.NumberInput

        super(MoneyIntervalField, self).__init__(*args, **kwargs)

        if max_value is not None:
            self.validators.append(validators.MaxValueValidator(max_value))
        if min_value is not None:
            self.validators.append(validators.MinValueValidator(min_value))

    def contribute_to_class(self, cls, name):
        # first, create the hidden fields. It is *crucial* that these
        # fields appears *before* the actual 'value' field (i.e. self) in
        # the models _meta.fields - to achieve this, we need to change it's
        # creation_counter class variable.
        interval_period_field = models.CharField(max_length=50,
            choices=MoneyInterval.get_intervals_for_widget(), editable=False,
            null=True, blank=True)
        # setting the counter to the same value as the date field itself will
        # ensure the precision field appear first - it is added first after all,
        # and when the date field is added later, it won't be sorted before it.
        interval_period_field.creation_counter = self.creation_counter
        cls.add_to_class(_interval_period_field_name(name), interval_period_field)

        per_interval_value_field = models.BigIntegerField(editable=False,
                                                          null=True, blank=True)
        # setting the counter to the same value as the date field itself will
        # ensure the precision field appear first - it is added first after all,
        # and when the date field is added later, it won't be sorted before it.
        per_interval_value_field.creation_counter = self.creation_counter
        cls.add_to_class(_per_interval_value_field_name(name), per_interval_value_field)


        # add the date field as normal
        super(MoneyIntervalField, self).contribute_to_class(cls, name)

        # as we are not using SubfieldBase (see intro), we need to do it's job
        # ourselves. we don't need to be generic, so don't use a metaclass, but
        # just assign the descriptor object here.
        setattr(cls, self.name, MoneyIntervalFieldCreator(self))

    def get_db_prep_save(self, value, connection):
        if isinstance(value, MoneyInterval): value = value.value
        return super(MoneyIntervalField, self).get_db_prep_save(value, connection)

    def get_db_prep_lookup(self, lookup_type, value):
        if lookup_type == 'exact':
            return [self.get_db_prep_save(value)]
        elif lookup_type == 'in':
            return [self.get_db_prep_save(v) for v in value]
        else:
            # let the base class deal with the rest
            return super(MoneyIntervalField, self).get_db_prep_lookup(lookup_type, value)

    def to_python(self, value):

        try:
            if isinstance(value, dict):
                mi = MoneyInterval(interval_period=value['earnings_interval_period'])
                mi.set_as_pennies(value['earnings_per_interval_value'])
            elif isinstance(value, MoneyInterval):
                return value
            else:
                mi = MoneyInterval(interval_period='per_month')
                mi.set_as_pennies(value)
            return mi
        except (TypeError, ValueError):
            raise exceptions.ValidationError(
                self.error_messages['invalid'],
                code='invalid',
                params={'value': value},
            )

    def clean(self, value, model_instance):
        value = self.to_python(value)
        self.validate(value, model_instance)
        #self.run_validators(value)
        return value

    def validate(self, value, model_instance):

        # Ideally the serialiser should validate this - the MoneyInterval class
        # wont initialise with an invalid value so that will have to do.
        #if not value.is_valid_interval_period(value.interval_period):
        #    raise exceptions.ValidationError(self.error_messages['invalid'], code='invalid')

        errors = []
        for v in self.validators:
            try:
                v(value.per_interval_value)
            except exceptions.ValidationError as e:
                if hasattr(e, 'code') and e.code in self.error_messages:
                    e.message = self.error_messages[e.code]
                errors.extend(e.error_list)

        if errors:
            raise exceptions.ValidationError(errors)


#     def formfield(self, **kwargs):
#         defaults = {'form_class': forms.FuzzyDateField}
#         defaults.update(kwargs)
#         return super(FuzzyDateField, self).formfield(**defaults)

    # Although we need flatten_data for (oldforms) admin, we don't need to
    # implement it here, as the DateField baseclass will just call strftime on
    # our FuzzyDate object, which is something we support.

 
add_introspection_rules([
    (
        [MoneyIntervalField], # Class(es) these apply to
        [],         # Positional arguments (not used)
        {           # Keyword argument
            #"min_value": ["min_value", {"default": None}],
            #"max_value": ["max_value", {"default": None}],
        },
    ),
], ["^legalaid\.fields\.MoneyIntervalField"])




