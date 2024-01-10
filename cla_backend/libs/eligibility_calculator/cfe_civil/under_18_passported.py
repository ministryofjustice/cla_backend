# Breaking the translate naming convention because attribute 'not_aggregated_no_income_low_capital' should belong to applicant object instead of assessment object.
def translate_under_18_passported(facts):
    if (hasattr(facts, "under_18_passported") and facts.under_18_passported) and (hasattr(facts, "is_you_under_18") and facts.is_you_under_18):
        return {"not_aggregated_no_income_low_capital": True}
    else:
        return {}
