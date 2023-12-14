def translate_applicant(applicant_facts):
    if hasattr(applicant_facts, "on_passported_benefits") and applicant_facts.on_passported_benefits:
        return {"receives_qualifying_benefit": applicant_facts.on_passported_benefits}
    else:
        return {}
