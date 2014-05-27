from legalaid.constants import CASELOGTYPE_SUBTYPES
from model_mommy.recipe import Recipe, seq, foreign_key

from ..models import Category, EligibilityCheck, Property, Savings, \
    Case, PersonalDetails, Income, Deductions, Person,\
    CaseLogType, CaseLog


category = Recipe(Category,
    name=seq('Name'), code=seq('Code'), order = seq(0)
)

person = Recipe(Person)

eligibility_check = Recipe(EligibilityCheck,
    category=foreign_key(category),
    dependants_young=5, dependants_old=6,
    you=foreign_key(person),
    partner=foreign_key(person)
)

from cla_common.helpers import MoneyInterval
mi = MoneyInterval('per_month', pennies=2200)

income = Recipe(Income, earnings=mi)
savings = Recipe(Savings)
deductions = Recipe(Deductions)

property = Recipe(Property,
    eligibility_check=foreign_key(eligibility_check)
)

personal_details = Recipe(PersonalDetails)

case = Recipe(Case,
    eligibility_check=foreign_key(eligibility_check),
    personal_details=foreign_key(personal_details)
)

logtype = Recipe(CaseLogType)

outcome_code = Recipe(CaseLogType, subtype=CASELOGTYPE_SUBTYPES.OUTCOME)
refsp_logtype = Recipe(CaseLogType, code='REFSP', subtype=CASELOGTYPE_SUBTYPES.OUTCOME)

case_log = Recipe(CaseLog,
    case=foreign_key(case),
    logtype=foreign_key(logtype)
)

