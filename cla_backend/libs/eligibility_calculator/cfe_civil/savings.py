from cla_backend.libs.eligibility_calculator.cfe_civil.conversions import pence_to_pounds


def _savings_value(value, description):
    if value > 0:
        return {
            "value": pence_to_pounds(value),
            "description": description,
            "subject_matter_of_dispute": False
        }
    else:
        return None


def translate_savings(savings_data):
    liquid_capital = []
    non_liquid_capital = []

    bank_value = _savings_value(savings_data.bank_balance, "Savings")
    invest_value = _savings_value(savings_data.investment_balance, "Investment")
    asset_value = _savings_value(savings_data.asset_balance, "Asset")

    if bank_value:
        liquid_capital.append(bank_value)
    if invest_value:
        liquid_capital.append(invest_value)
    if asset_value:
        non_liquid_capital.append(asset_value)
    return dict(capitals={
        "bank_accounts": liquid_capital,
        "non_liquid_capital": non_liquid_capital
    })
