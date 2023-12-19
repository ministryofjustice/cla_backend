from cla_backend.libs.eligibility_calculator.cfe_civil.conversions import pence_to_pounds, has_all_attributes

_OUTGOING_CATEGORY_TO_REGULAR_TRANSACTION = {
    "maintenance": "maintenance_out",
    "childcare": "child_care",
    "mortgage": "rent_or_mortgage",
    "rent": "rent_or_mortgage",
    "criminal_legalaid_contributions": "legal_aid",
}


class DeductionsTranslator(object):
    def __init__(self, deductions):
        self._deductions = deductions

    def is_complete(self):
        return has_all_attributes(self._deductions, _OUTGOING_CATEGORY_TO_REGULAR_TRANSACTION.keys())

    def translate(self):
        regular_transactions = []

        for outgoing_category, cfe_category in _OUTGOING_CATEGORY_TO_REGULAR_TRANSACTION.items():
            if hasattr(self._deductions, outgoing_category):
                amount_pence = getattr(self._deductions, outgoing_category)
                if amount_pence:
                    regular_transactions.append(
                        {
                            "category": cfe_category,
                            "operation": "debit",
                            "frequency": "monthly",
                            "amount": pence_to_pounds(amount_pence)
                        }
                    )
        return {"regular_transactions": regular_transactions}
