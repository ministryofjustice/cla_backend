import datetime


def translate_age(today, facts):
    # in keeping with CCQ behaviour, we choose 70 to mean 'over 60'
    # 50 to mean 'under 60, over 18' and 17 to mean 'under 18'. These numbers are all arbitrary
    # as long as they are in the appropriate range - CFE wants a date of birth which we don't have
    if hasattr(facts, "is_you_or_your_partner_over_60") and facts.is_you_or_your_partner_over_60:
        age = 70
    elif hasattr(facts, "is_you_under_18") and facts.is_you_under_18:
        age = 17
    else:
        age = 50
    date_of_birth = datetime.date(today.year - age, today.month, today.day)
    return {"date_of_birth": str(date_of_birth)}
