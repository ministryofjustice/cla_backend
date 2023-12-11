import datetime


def translate_age(today, facts):
    if hasattr(facts, "is_you_or_your_partner_over_60") and facts.is_you_or_your_partner_over_60:
        age = 70
    elif hasattr(facts, "is_you_under_18") and facts.is_you_under_18:
        age = 17
    else:
        age = 50
    date_of_birth = datetime.date(today.year - age, today.month, today.day)
    return {'applicant': {'date_of_birth': str(date_of_birth)}}
