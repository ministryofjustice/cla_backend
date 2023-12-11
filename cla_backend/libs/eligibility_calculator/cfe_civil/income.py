from cla_backend.libs.eligibility_calculator.cfe_civil.conversions import pence_to_pounds


def translate_income(income_data):
    regular_transactions = []  # pension, maintenance_received, benefits

    if income_data.tax_credits > 0:
        regular_transactions.append(regular_transaction("benefits", income_data.tax_credits))

    if income_data.maintenance_received > 0:
        regular_transactions.append(regular_transaction("maintenance_in", income_data.maintenance_received))

    if income_data.pension > 0:
        regular_transactions.append(regular_transaction("pension", income_data.pension))

    if income_data.benefits > 0:
        regular_transactions.append(regular_transaction("benefits", income_data.benefits))

    if income_data.child_benefits > 0:
        regular_transactions.append(regular_transaction("benefits", income_data.child_benefits))

    if income_data.other_income > 0:
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
