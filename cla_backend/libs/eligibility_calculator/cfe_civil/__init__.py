# translate bank_balance, investment_balance and asset_balance from CLA into CFE format
# credit_balance isn't captured (and sounds like a credit card balance) which is not part of eligibility calculations


def translate_savings(savings_data):
    liquid_capital = []
    non_liquid_capital = []
    if savings_data.bank_balance > 0:
        liquid_capital.append(
            {
                "value": savings_data.bank_balance,
                "description": "Savings Account",
                "subject_matter_of_dispute": False
            })
    if savings_data.investment_balance > 0:
        liquid_capital.append(
            {
                "value": savings_data.investment_balance,
                "description": "Investment",
                "subject_matter_of_dispute": False
            })
    if savings_data.asset_balance > 0:
        non_liquid_capital.append(
            {
                "value": savings_data.asset_balance,
                "description": "Asset",
                "subject_matter_of_dispute": False
            })
    value = dict(capitals={
        "bank_accounts": liquid_capital,
        "non_liquid_capital": non_liquid_capital
    })
    return value
