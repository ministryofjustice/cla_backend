from cla_backend.libs.eligibility_calculator.cfe_civil.conversions import pence_to_pounds

logger = __import__("logging").getLogger(__name__)


# fields in both CFE's employment_details and self_employment_details sections
def _common_income_fields(gross, deductions):
    return {
        "gross": gross,
        "tax": -pence_to_pounds(deductions.income_tax) if hasattr(deductions, "income_tax") else 0,
        "frequency": "monthly",
        "prisoner_levy": 0,
        "student_debt_repayment": 0,
        "national_insurance": -pence_to_pounds(deductions.national_insurance) if hasattr(deductions, "national_insurance") else 0,
    }


def translate_employment(income, deductions):
    gross = 0
    if hasattr(income, "earnings"):
        gross = pence_to_pounds(income.earnings)
    if hasattr(income, "self_employment_drawings"):
        gross += pence_to_pounds(income.self_employment_drawings)

    if (
        gross == 0
        and (not hasattr(deductions, "income_tax") or deductions.income_tax == 0)
        and (not hasattr(deductions, "national_insurance") or deductions.national_insurance == 0)
    ):
        return {"employment_details": []}

    fields = _common_income_fields(gross, deductions)
    if hasattr(income, "self_employed") and income.self_employed:
        return {"self_employment_details": [{"income": fields}]}
    else:
        fields.update(
            {
                "receiving_only_statutory_sick_or_maternity_pay": False,
                "benefits_in_kind": 0,
            }
        )
        return {"employment_details": [{"income": fields}]}
