def translate_applicant(applicant_facts):
    applicant = {
        "date_of_birth": "1992-07-25",
        "receives_qualifying_benefit": False,
        "receives_asylum_support": False,
    }
    if hasattr(applicant_facts, "on_passported_benefits") and applicant_facts.on_passported_benefits:
        applicant["receives_qualifying_benefit"] = applicant_facts.on_passported_benefits
    value = dict(
        applicant=applicant
    )
    return value
