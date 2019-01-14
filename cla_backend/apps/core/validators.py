from django.core.exceptions import ValidationError


def validate_first_of_month(value):
    if value.day != 1:
        raise ValidationError("%s should only be first day of the month." % value)
