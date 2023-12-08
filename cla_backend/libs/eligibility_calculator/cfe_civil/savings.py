from cla_backend.libs.eligibility_calculator.cfe_civil.conversions import pence_to_pounds


def translate_savings(savings_data):
    liquid_capital = []
    non_liquid_capital = []
    if savings_data.bank_balance > 0:
        liquid_capital.append(
            {
                "value": pence_to_pounds(savings_data.bank_balance),
                "description": "Savings",
                "subject_matter_of_dispute": False
            })
    if savings_data.investment_balance > 0:
        liquid_capital.append(
            {
                "value": pence_to_pounds(savings_data.investment_balance),
                "description": "Investment",
                "subject_matter_of_dispute": False
            })
    if savings_data.asset_balance > 0:
        non_liquid_capital.append(
            {
                "value": pence_to_pounds(savings_data.asset_balance),
                "description": "Asset",
                "subject_matter_of_dispute": False
            })
    value = dict(capitals={
        "bank_accounts": liquid_capital,
        "non_liquid_capital": non_liquid_capital
    })
    return value
