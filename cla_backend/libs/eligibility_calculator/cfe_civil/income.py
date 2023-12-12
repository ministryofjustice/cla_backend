from cla_backend.libs.eligibility_calculator.cfe_civil.conversions import pence_to_pounds


def translate_income(income_data):
    regular_transactions = []  # pension, maintenance_received, benefits

    if hasattr(income_data, "tax_credits") and income_data.tax_credits > 0:
        regular_transactions.append(regular_transaction("benefits", income_data.tax_credits))

    if hasattr(income_data, "maintenance_received") and income_data.maintenance_received > 0:
        regular_transactions.append(regular_transaction("maintenance_in", income_data.maintenance_received))

    if hasattr(income_data, "pension") and income_data.pension > 0:
        regular_transactions.append(regular_transaction("pension", income_data.pension))

    if hasattr(income_data, "benefits") and income_data.benefits > 0:
        regular_transactions.append(regular_transaction("benefits", income_data.benefits))

    if hasattr(income_data, "child_benefits") and income_data.child_benefits > 0:
        regular_transactions.append(regular_transaction("benefits", income_data.child_benefits))

    if hasattr(income_data, "other_income") and income_data.other_income > 0:
        regular_transactions.append(regular_transaction("friends_or_family", income_data.other_income))

    value = dict(
        regular_transactions=regular_transactions
    )
    return value


def regular_transaction(category, amount):
    return {
        "category": category,
        "operation": "credit",
        "frequency": "monthly",
        "amount": pence_to_pounds(amount),
    }
