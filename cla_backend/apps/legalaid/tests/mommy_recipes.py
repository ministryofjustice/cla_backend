from model_mommy.recipe import Recipe, seq, foreign_key

from cla_common.money_interval.models import MoneyInterval

from ..models import Category, EligibilityCheck, Property, Savings, \
    Case, PersonalDetails, Income, Deductions, Person,\
    ThirdPartyDetails, AdaptationDetails


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


income = Recipe(Income, earnings=MoneyInterval('per_month', pennies=2200),
                other_income=MoneyInterval('per_week', pennies=2200)
                )
savings = Recipe(Savings)
deductions = Recipe(Deductions,
                    income_tax = MoneyInterval('per_week', pennies=2200),
                    national_insurance = MoneyInterval('per_4week', pennies=2200),
                    maintenance = MoneyInterval('per_year', pennies=2200),
                    childcare = MoneyInterval('per_week', pennies=2200),
                    mortgage = MoneyInterval('per_week', pennies=2200),
                    rent = MoneyInterval('per_week', pennies=2200)
                    )

property = Recipe(Property,
    eligibility_check=foreign_key(eligibility_check)
)

personal_details = Recipe(PersonalDetails,
                          mobile_phone=seq(555),
                          home_phone=seq(7777),
                          title='Dr',
                          street=seq('Street'),
                          postcode=seq('postcode'),
                          full_name=seq('fullname'))

thirdparty_details = Recipe(ThirdPartyDetails,
                          personal_details=foreign_key(personal_details)
                          )

adaptation_details = Recipe(AdaptationDetails)


case = Recipe(Case,
    eligibility_check=foreign_key(eligibility_check),
    personal_details=foreign_key(personal_details)
)




