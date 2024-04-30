from cla_backend.libs.eligibility_calculator.cfe_civil.conversions import pence_to_pounds, none_filter


def _savings_value(value, description, subject_matter_of_dispute):
    if value > 0:
        return {
            "value": pence_to_pounds(value),
            "description": description,
            "subject_matter_of_dispute": subject_matter_of_dispute,
        }


def translate_savings(savings_data, subject_matter_of_dispute=False):
    liquid_capital = []
    liquid_capital.append(_savings_value(savings_data.bank_balance, "Savings", subject_matter_of_dispute))
    liquid_capital.append(_savings_value(savings_data.investment_balance, "Investment", subject_matter_of_dispute))

    non_liquid_capital = []
    non_liquid_capital.append(
        _savings_value(
            savings_data.asset_balance, "Valuable items worth over 500 pounds", subject_matter_of_dispute
        )
    )
    non_liquid_capital.append(
        _savings_value(savings_data.credit_balance, "Credit balance", subject_matter_of_dispute)
    )

    return {
        "capitals": {
            "bank_accounts": none_filter(liquid_capital),
            "non_liquid_capital": none_filter(non_liquid_capital),
        }
    }
