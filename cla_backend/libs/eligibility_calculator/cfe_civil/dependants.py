import datetime

_DEPENDANTS_KEY = "dependants"


def has_dependants_key(dict):
    return _DEPENDANTS_KEY in dict


def _dependant_aged(todays_date, age, relationship):
    return dict(date_of_birth=str(datetime.date(todays_date.year - age, todays_date.month, todays_date.day)),
                in_full_time_education=False,
                relationship=relationship,
                income=dict(frequency="weekly", amount=0),
                assets_value=0)


def translate_dependants(todays_date, facts):
    if hasattr(facts, "dependants_young"):
        children = [_dependant_aged(todays_date, 15, "child_relative") for _ in range(facts.dependants_young)]
    else:
        children = []
    if hasattr(facts, "dependants_old"):
        adults = [_dependant_aged(todays_date, 17, "adult_relative") for _ in range(facts.dependants_old)]
    else:
        adults = []
    return {_DEPENDANTS_KEY: children + adults}
