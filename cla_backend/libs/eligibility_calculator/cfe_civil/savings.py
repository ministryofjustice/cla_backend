from cla_backend.libs.eligibility_calculator.cfe_civil.conversions import pence_to_pounds, none_filter


def _savings_value(value, description):
    if value > 0:
        return {
            "value": pence_to_pounds(value),
            "description": description,
            "subject_matter_of_dispute": False
        }


def translate_savings(savings_data):
    liquid_capital = [
        _savings_value(savings_data.bank_balance, "Savings"),
        _savings_value(savings_data.investment_balance, "Investment")
    ]
    non_liquid_capital = [
        _savings_value(savings_data.asset_balance, "Asset")
    ]

    return dict(capitals={
        "bank_accounts": none_filter(liquid_capital),
        "non_liquid_capital": none_filter(non_liquid_capital)
    })
