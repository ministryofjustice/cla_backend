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


_EMPLOYMENT_KEY = "employment_details"
_SELF_EMPLOYMENT_KEY = "self_employment_details"


class EmploymentTranslator(object):
    def __init__(self, income, deductions):
        self._income = income
        self._deductions = deductions

    def is_complete(self):
        return _all_income_fields(self._income) and _all_deductions_fields(self._deductions)

    def translate(self):
        fields = _common_income_fields(self._income, self._deductions)
        if self._income.self_employed:
            return {
                _SELF_EMPLOYMENT_KEY: [
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
                _EMPLOYMENT_KEY: [
                    {
                        "income": fields
                    }
                ]
            }
