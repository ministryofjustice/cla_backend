from cla_backend.libs.eligibility_calculator.cfe_civil.conversions import pence_to_pounds


def translate_income(income_data):
    regular_transactions = []  # pension, maintenance_received, benefits

    if not income_data.self_employed and (income_data.earnings > 0):
        print("employment_income, employment_details")

    if income_data.self_employed and (income_data.self_employment_drawings > 0):
        print("self_employment_details")

    if income_data.tax_credits > 0:
        print("?")
        regular_transactions.append(
            {
                "category": "benefits",
                "operation": "credit",
                "frequency": "monthly",
                "amount": pence_to_pounds(income_data.tax_credits),
            })

    if income_data.maintenance_received > 0:
        print("cash_transactions, other_incomes, regular_transactions")
        regular_transactions.append(
            {
                "category": "maintenance_in",
                "operation": "credit",
                "frequency": "monthly",
                "amount": pence_to_pounds(income_data.maintenance_received),
            })

    if income_data.pension > 0:
        print("cash_transactions, other_incomes, regular_transactions")
        regular_transactions.append(
            {
                "category": "pension_contribution",
                "operation": "credit",
                "frequency": "monthly",
                "amount": pence_to_pounds(income_data.pension),
            })

    if income_data.benefits > 0:
        print("cash_transactions, other_incomes, regular_transactions, state_benefits")
        regular_transactions.append(
            {
                "category": "benefits",
                "operation": "credit",
                "frequency": "monthly",
                "amount": pence_to_pounds(income_data.benefits),
            })

    if income_data.child_benefits > 0:
        print("?")
        regular_transactions.append(
            {
                "category": "child_care",
                "operation": "credit",
                "frequency": "monthly",
                "amount": pence_to_pounds(income_data.child_benefits),
            })

    if income_data.other_income > 0:
        print("?")
        regular_transactions.append(
            {
                "category": "friends_or_family",
                "operation": "credit",
                "frequency": "monthly",
                "amount": pence_to_pounds(income_data.other_income),
            })

    value = dict(
        regular_transactions=regular_transactions
    )
    return value
