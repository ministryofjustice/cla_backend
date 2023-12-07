
def translate_income(income_data):
    cash_transactions = {"income": []}   # pension, maintenance_received, benefits
    employment_income = [{"payments": []}]
    irregular_incomes = {"payments": []}
    other_incomes = [{"payments": []}]   # pension, maintenance_received, benefits
    regular_transactions = []   # pension, maintenance_received, benefits
    state_benefits = [{"payments": []}]   # benefits
    employment_details = [{"income": {}}]   # earnings
    self_employment_details = [{"income": {}}]   # self_employment_drawings

    if not(income_data.self_employed) and (income_data.earnings > 0):
        print("employment_income, employment_details")

    if income_data.self_employed and (income_data.self_employment_drawings > 0):
        print("self_employment_details")

    if income_data.benefits > 0:
        print("cash_transactions, other_incomes, regular_transactions, state_benefits")

    if income_data.tax_credits > 0:
        print("?")

    if income_data.child_benefits > 0:
        print("?")

    if income_data.maintenance_received > 0:
        print("cash_transactions, other_incomes, regular_transactions")

    if income_data.pension > 0:
        print("cash_transactions, other_incomes, regular_transactions")

    if income_data.other_income > 0:
        print("?")

    value = dict(
        cash_transactions=cash_transactions,
        employment_income=employment_income,
        irregular_incomes=irregular_incomes,
        other_incomes=other_incomes,
        regular_transactions=regular_transactions,
        state_benefits=state_benefits,
        employment_details=employment_details,
        self_employment_details=self_employment_details
    )
    return value
