def translate_income(income, deductions):
    value = {
            "income": {
                "receiving_only_statutory_sick_or_maternity_pay": False,
                "frequency": "monthly",
                "gross": income.earnings,
                "benefits_in_kind": 0,
                "tax": deductions.income_tax,
                "national_insurance": deductions.national_insurance,
                "prisoner_levy": 0,
                "student_debt_repayment": 0
            }
    }
    if income.self_employed:
        return {
            "self_employment_details": [ value ]
        }
    else:
        return {
            "employment_details": [ value ]
        }
