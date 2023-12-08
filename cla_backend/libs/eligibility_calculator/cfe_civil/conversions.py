from decimal import Decimal


def pence_to_pounds(pence):
    decimal_value = (Decimal(pence) / 100).quantize(Decimal(".01"))
    return float(decimal_value)
