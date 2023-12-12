from cla_backend.libs.eligibility_calculator.cfe_civil.conversions import pence_to_pounds


def translate_income(income_data):
    regular_transactions = [
        _regular_transaction("benefits", income_data, "tax_credits"),
        _regular_transaction("maintenance_in", income_data, "maintenance_received"),
        _regular_transaction("pension", income_data, "pension"),
        _regular_transaction("benefits", income_data, "benefits"),
        _regular_transaction("benefits", income_data, "child_benefits"),
        _regular_transaction("friends_or_family", income_data, "other_income")
    ]

    value = dict(
        regular_transactions=[x for x in regular_transactions if x is not None]
    )
    return value


def _regular_transaction(cfe_category, income_data, attr_name):
    if hasattr(income_data, attr_name) and getattr(income_data, attr_name) > 0:
        return {
            "category": cfe_category,
            "operation": "credit",
            "frequency": "monthly",
            "amount": pence_to_pounds(getattr(income_data, attr_name))
        }
