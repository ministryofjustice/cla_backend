from decimal import Decimal


def pence_to_pounds(pence):
    if pence is None:
        return 0
    else:
        decimal_value = (Decimal(pence) / 100).quantize(Decimal(".01"))
        return float(decimal_value)


def none_filter(array):
    return [x for x in array if x is not None]
