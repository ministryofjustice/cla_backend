def translate_applicant(applicant_facts):
    cfe_applicant = {}

    if applicant_facts.on_passported_benefits:
        cfe_applicant["receives_qualifying_benefit"] = applicant_facts.on_passported_benefits

    if applicant_facts.on_nass_benefits:
        cfe_applicant["receives_asylum_support"] = applicant_facts.on_nass_benefits

    return cfe_applicant
