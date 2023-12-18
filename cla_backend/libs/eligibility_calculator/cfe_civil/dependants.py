import datetime

_DEPENDANTS_KEY = "dependants"


def has_dependants_key(dict):
    return _DEPENDANTS_KEY in dict


def translate_dependants(todays_date, facts):
    dependants = []
    if hasattr(facts, "dependants_young"):
        for child in range(facts.dependants_young):
            dependants.append(
                dict(date_of_birth=str(datetime.date(todays_date.year - 15, todays_date.month, todays_date.day)),
                     in_full_time_education=False,
                     relationship="child_relative",
                     income=dict(frequency="weekly", amount=0),
                     assets_value=0),
            )
    if hasattr(facts, "dependants_old"):
        for adult in range(facts.dependants_old):
            dependants.append(
                dict(date_of_birth=str(datetime.date(todays_date.year - 17, todays_date.month, todays_date.day)),
                     in_full_time_education=False,
                     relationship="adult_relative",
                     income=dict(frequency="weekly", amount=0),
                     assets_value=0),
            )
    return {_DEPENDANTS_KEY: dependants}
