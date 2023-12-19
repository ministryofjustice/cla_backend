from cla_backend.libs.eligibility_calculator.cfe_civil.conversions import pence_to_pounds, none_filter, \
    has_all_attributes


def _savings_value(value, description):
    if value > 0:
        return {
            "value": pence_to_pounds(value),
            "description": description,
            "subject_matter_of_dispute": False
        }


class SavingsTranslator(object):
    def __init__(self, savings_data):
        self._savings_data = savings_data

    def is_complete(self):
        return has_all_attributes(self._savings_data, ["bank_balance", "investment_balance", "asset_balance"])

    def translate(self):
        liquid_capital = [
            _savings_value(self._savings_data.bank_balance, "Savings"),
            _savings_value(self._savings_data.investment_balance, "Investment")
        ]
        non_liquid_capital = [
            _savings_value(self._savings_data.asset_balance, "Valuable items worth over 500 pounds")
        ]

        return {
            "capitals": {
                "bank_accounts": none_filter(liquid_capital),
                "non_liquid_capital": none_filter(non_liquid_capital)
            }
        }
