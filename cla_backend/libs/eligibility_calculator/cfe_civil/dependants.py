from dateutil.relativedelta import relativedelta


def _dependant_aged(todays_date, age, relationship):
    return dict(
        date_of_birth=str(todays_date - relativedelta(years=age)),
        in_full_time_education=False,
        relationship=relationship,
        income=dict(amount=0, frequency="weekly"),  # assume the dependant has no income
        assets_value=0,
    )


def translate_dependants(todays_date, facts):
    if hasattr(facts, "dependants_young"):
        children = [_dependant_aged(todays_date, 15, "child_relative") for _ in range(facts.dependants_young)]
    else:
        children = []
    if hasattr(facts, "dependants_old"):
        adults = [_dependant_aged(todays_date, 17, "adult_relative") for _ in range(facts.dependants_old)]
    else:
        adults = []
    return {"dependants": children + adults}
