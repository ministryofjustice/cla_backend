from cla_backend.libs.eligibility_calculator.cfe_civil.conversions import pence_to_pounds, none_filter


def _savings_value(savings_data, attr, description):
    if hasattr(savings_data, attr):
        return {
            "value": pence_to_pounds(getattr(savings_data, attr)),
            "description": description,
            "subject_matter_of_dispute": False
        }


_CFE_SAVINGS_KEY = "capitals"


def has_savings_key(request_data):
    return _CFE_SAVINGS_KEY in request_data


def translate_savings(savings_data):
    liquid = [
        _savings_value(savings_data, "bank_balance", "Savings"),
        _savings_value(savings_data, "investment_balance", "Investment")
    ]
    non_liquid = [
        _savings_value(savings_data, "asset_balance", "Valuable items worth over 500 pounds")
    ]
    liquid_capital = none_filter(liquid)
    non_liquid_capital = none_filter(non_liquid)

    # all fields have to be set
    if len(liquid_capital) + len(non_liquid_capital) < len(liquid) + len(non_liquid):
        return {}
    else:
        return {
            _CFE_SAVINGS_KEY: {
                "bank_accounts": liquid_capital,
                "non_liquid_capital": non_liquid_capital
            }
        }
