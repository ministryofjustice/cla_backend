from decimal import Decimal


def pence_to_pounds(pence):
    decimal_value = (Decimal(pence) / 100).quantize(Decimal(".01"))
    return float(decimal_value)


def none_filter(array):
    return [x for x in array if x is not None]


def has_all_attributes(object, attr_list):
    present = [hasattr(object, attr) for attr in attr_list]
    return len([x for x in present if x is False]) == 0


def missing_attributes(object, expected_attributes):
    for attr in expected_attributes:
        if not hasattr(object, attr):
            return attr
