
def translate_savings(savings_data):
    liquid_capital = []
    non_liquid_capital = []
    if savings_data.bank_balance > 0:
        liquid_capital.append(
            {
                "value": savings_data.bank_balance / 100,
                "description": "Savings",
                "subject_matter_of_dispute": False
            })
    if savings_data.investment_balance > 0:
        liquid_capital.append(
            {
                "value": savings_data.investment_balance / 100,
                "description": "Investment",
                "subject_matter_of_dispute": False
            })
    if savings_data.asset_balance > 0:
        non_liquid_capital.append(
            {
                "value": savings_data.asset_balance / 100,
                "description": "Asset",
                "subject_matter_of_dispute": False
            })
    value = dict(capitals={
        "bank_accounts": liquid_capital,
        "non_liquid_capital": non_liquid_capital
    })
    return value
