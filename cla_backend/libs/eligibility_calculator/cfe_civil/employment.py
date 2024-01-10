from cla_backend.libs.eligibility_calculator.cfe_civil.conversions import missing_attributes, pence_to_pounds

logger = __import__("logging").getLogger(__name__)


def _are_there_missing_deductions_fields(deductions):
    missing_attr = missing_attributes(deductions, ["income_tax", "national_insurance"])
    if missing_attr:
        logger.error(
            "Missing field in deductions: '%s'. Ignoring all (self) employment income and deductions!" % missing_attr
        )
        return True


def _are_there_missing_income_fields(incomes):
    missing_attr = missing_attributes(incomes, ["earnings", "self_employed"])
    if missing_attr:
        logger.error(
            "Missing field in incomes: '%s'. Ignoring all (self) employment income and deductions!" % missing_attr
        )
        return True


# fields in both CFE's employment_details and self_employment_details sections
def _common_income_fields(gross, deductions):
    return {
        "gross": gross,
        "tax": -pence_to_pounds(deductions.income_tax),
        "frequency": "monthly",
        "prisoner_levy": 0,
        "student_debt_repayment": 0,
        "national_insurance": -pence_to_pounds(deductions.national_insurance),
    }


def translate_employment(income, deductions):
    if _are_there_missing_income_fields(income) or _are_there_missing_deductions_fields(deductions):
        return {}

    gross = pence_to_pounds(income.earnings)
    if hasattr(income, "self_employment_drawings"):
        gross += pence_to_pounds(income.self_employment_drawings)

    if gross == 0 and deductions.income_tax == 0 and deductions.national_insurance == 0:
        return {"employment_details": []}

    fields = _common_income_fields(gross, deductions)
    if income.self_employed:
        return {"self_employment_details": [{"income": fields}]}
    else:
        fields.update(
            {
                "receiving_only_statutory_sick_or_maternity_pay": False,
                "benefits_in_kind": 0,
            }
        )
        return {"employment_details": [{"income": fields}]}
