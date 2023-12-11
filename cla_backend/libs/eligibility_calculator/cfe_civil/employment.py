from cla_backend.libs.eligibility_calculator.cfe_civil.conversions import has_all_attributes


def _all_deductions_fields(deductions):
    return has_all_attributes(deductions, ["income_tax", "national_insurance"])


def _all_income_fields(incomes):
    return has_all_attributes(incomes, ["earnings", "self_employed"])


def _common_income_fields(income, deductions):
    return {
        "gross": income.earnings / 100,
        "tax": -deductions.income_tax / 100,
        "frequency": "monthly",
        "prisoner_levy": 0,
        "student_debt_repayment": 0,
        "national_insurance": -deductions.national_insurance / 100
    }


def translate_employment(income, deductions):
    if _all_income_fields(income) and _all_deductions_fields(deductions):
        fields = _common_income_fields(income, deductions)
        if income.self_employed:
            return {
                "self_employment_details": [
                    {
                        "income": fields
                    }
                ]
            }
        else:
            fields.update({
                "receiving_only_statutory_sick_or_maternity_pay": False,
                "benefits_in_kind": 0,
            })
            return {
                "employment_details": [
                    {
                        "income": fields
                    }
                ]
            }
    else:
        return {}
