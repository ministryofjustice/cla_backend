from cla_backend.libs.eligibility_calculator.cfe_civil.conversions import pence_to_pounds


INCOME_CATEGORY_TO_REGULAR_TRANSACTION = {
    "tax_credits": "benefits",
    "maintenance_received": "maintenance_in",
    "pension": "pension",
    "benefits": "benefits",
    "child_benefits": "benefits",
    "other_income": "friends_or_family",
}


def translate_income(income_data):
    regular_transactions = []

    for income_category in INCOME_CATEGORY_TO_REGULAR_TRANSACTION:
        if hasattr(income_data, income_category):
            amount_pence = getattr(income_data, income_category)
            regular_transactions.append(
                {
                    "category": INCOME_CATEGORY_TO_REGULAR_TRANSACTION[income_category],
                    "operation": "credit",
                    "frequency": "monthly",
                    "amount": pence_to_pounds(amount_pence),
                }
            )
    non_zero_transactions = [x for x in regular_transactions if x["amount"] > 0]
    return {"regular_transactions": non_zero_transactions}
