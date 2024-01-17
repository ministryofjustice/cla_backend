from dateutil.relativedelta import relativedelta


def translate_age(today, facts):
    # in keeping with CCQ behaviour, we choose 70 to mean 'over 60'
    # 50 to mean 'under 60, over 18' and 17 to mean 'under 18'. These numbers are all arbitrary
    # as long as they are in the appropriate range - CFE wants a date of birth which we don't have
    if facts.is_you_or_your_partner_over_60:
        age = 70
    elif facts.is_you_under_18:
        age = 17
    else:
        age = 50
    date_of_birth = today - relativedelta(years=age)
    return {"date_of_birth": str(date_of_birth)}
