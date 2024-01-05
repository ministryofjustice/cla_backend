def translate_assessment(facts):
    if hasattr(facts, "under_18_passported") and hasattr(facts, "is_you_under_18"):
        return {"not_aggregated_no_income_low_capital": facts.under_18_passported and facts.is_you_under_18}
    else:
        return {}
