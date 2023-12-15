from collections import defaultdict

from cla_backend.libs.eligibility_calculator.cfe_civil.conversions import pence_to_pounds


def translate_savings(savings_data):

    def _savings_value(value_pence, description):
        return {
            "value": pence_to_pounds(value_pence),
            "description": description,
            "subject_matter_of_dispute": False
        }

    capitals = defaultdict(list)  # A convenience - a new key has defaults value of [], ready to append to

    if hasattr(savings_data, "bank_balance") and savings_data.bank_balance > 0:
        capitals["bank_accounts"].append(
            _savings_value(savings_data.bank_balance, "Bank balance")
        )

    if hasattr(savings_data, "investment_balance") and savings_data.investment_balance > 0:
        capitals["bank_accounts"].append(
            _savings_value(savings_data.investment_balance, "Investment")
        )

    if hasattr(savings_data, "asset_balance") and savings_data.asset_balance > 0:
        capitals["non_liquid_capital"].append(
            _savings_value(savings_data.asset_balance, "Asset")
        )

    return {"capitals": capitals} if capitals else {}
