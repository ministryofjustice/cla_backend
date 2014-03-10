from model_mommy.recipe import Recipe, seq, foreign_key

from ..models import Category, EligibilityCheck, Property, Savings, \
    Case, PersonalDetails, Income, Deductions, Person


category = Recipe(Category,
    name=seq('Name'), order = seq(0)
)

person = Recipe(Person)

eligibility_check = Recipe(EligibilityCheck,
    category=foreign_key(category),
    dependants_young=5, dependants_old=6,
    you=foreign_key(person),
    partner=foreign_key(person)
)

income = Recipe(Income)
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
