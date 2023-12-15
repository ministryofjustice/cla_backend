def translate_applicant(applicant_facts):
    if hasattr(applicant_facts, "on_passported_benefits") and applicant_facts.on_passported_benefits:
        return {"receives_qualifying_benefit": applicant_facts.on_passported_benefits}

    if hasattr(applicant_facts, "on_nass_benefits") and applicant_facts.on_nass_benefits:
        return {"receives_asylum_support": applicant_facts.on_nass_benefits}

    else:
        return {}
