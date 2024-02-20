from cla_backend.libs.eligibility_calculator.cfe_civil.conversions import pence_to_pounds

logger = __import__("logging").getLogger(__name__)


_OUTGOING_CATEGORY_TO_REGULAR_TRANSACTION = {
    "maintenance": "maintenance_out",
    "childcare": "child_care",
    "mortgage": "rent_or_mortgage",
    "rent": "rent_or_mortgage",
    "criminal_legalaid_contributions": "legal_aid",
}


def translate_deductions(deductions):
    regular_transactions = []

    for outgoing_category, cfe_category in _OUTGOING_CATEGORY_TO_REGULAR_TRANSACTION.items():
        amount_pence = getattr(deductions, outgoing_category)
        if amount_pence:
            regular_transactions.append(
                {
                    "category": cfe_category,
                    "operation": "debit",
                    "frequency": "monthly",
                    "amount": pence_to_pounds(amount_pence),
                }
            )

    return {"regular_transactions": regular_transactions}
