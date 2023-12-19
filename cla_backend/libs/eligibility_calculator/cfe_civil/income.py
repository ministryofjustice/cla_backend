from cla_backend.libs.eligibility_calculator.cfe_civil.conversions import pence_to_pounds, has_all_attributes

_INCOME_CATEGORY_TO_REGULAR_TRANSACTION = {
    "tax_credits": "benefits",
    "maintenance_received": "maintenance_in",
    "pension": "pension",
    "benefits": "benefits",
    "child_benefits": "benefits",
    "other_income": "friends_or_family",
}

_CFE_INCOME_KEY = "regular_transactions"


class NonEmploymentIncomeTranslator(object):
    def __init__(self, income_data):
        self._income_data = income_data

    def is_complete(self):
        return has_all_attributes(self._income_data, _INCOME_CATEGORY_TO_REGULAR_TRANSACTION.keys())

    def translate(self):
        regular_transactions = []

        for income_category, cfe_category in _INCOME_CATEGORY_TO_REGULAR_TRANSACTION.items():
            if hasattr(self._income_data, income_category):
                amount_pence = getattr(self._income_data, income_category)
                regular_transactions.append(
                    {
                        "category": cfe_category,
                        "operation": "credit",
                        "frequency": "monthly",
                        "amount": pence_to_pounds(amount_pence)
                    }
                )
        non_zero_transactions = [x for x in regular_transactions if x['amount'] > 0]
        return {_CFE_INCOME_KEY: non_zero_transactions}
