def translate_applicant(applicant_facts):
    cfe_applicant = {}

    if hasattr(applicant_facts, "on_passported_benefits") and applicant_facts.on_passported_benefits:
        cfe_applicant["receives_qualifying_benefit"] = applicant_facts.on_passported_benefits

    if hasattr(applicant_facts, "on_nass_benefits") and applicant_facts.on_nass_benefits:
        cfe_applicant["receives_asylum_support"] = applicant_facts.on_nass_benefits

    return cfe_applicant
