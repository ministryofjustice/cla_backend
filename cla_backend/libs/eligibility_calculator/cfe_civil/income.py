def translate_income(income, deductions):
    if hasattr(income, "self_employed") and income.self_employed:
        result = {
            "self_employment_details": [
                {
                    "income": {
                        "frequency": "monthly",
                        "gross": income.earnings / 100,
                        "tax": -deductions.income_tax / 100,
                        "national_insurance": -deductions.national_insurance / 100,
                        "prisoner_levy": 0,
                        "student_debt_repayment": 0
                    }
                }
            ]
        }
    else:
        result = {
            "employment_details": [
                {
                    "income": {
                        "receiving_only_statutory_sick_or_maternity_pay": False,
                        "frequency": "monthly",
                        "gross": income.earnings / 100,
                        "benefits_in_kind": 0,
                        "tax": -deductions.income_tax / 100,
                        "national_insurance": -deductions.national_insurance / 100,
                        "prisoner_levy": 0,
                        "student_debt_repayment": 0
                    }}
            ]
        }
    return result
