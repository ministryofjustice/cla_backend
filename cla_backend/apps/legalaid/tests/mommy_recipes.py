from model_mommy.recipe import Recipe, seq, foreign_key

from cla_common.money_interval.models import MoneyInterval

from diagnosis.tests.mommy_recipes import diagnosis_yes

from ..models import (
    Category,
    EligibilityCheck,
    Property,
    Savings,
    Case,
    PersonalDetails,
    Income,
    Deductions,
    Person,
    ThirdPartyDetails,
    AdaptationDetails,
    MatterType,
    MediaCode,
    MediaCodeGroup,
    CaseNotesHistory,
    EODDetails,
    EODDetailsCategory,
)

category = Recipe(Category, name=seq("Name"), code=seq("Code"), order=seq(0))

income = Recipe(
    Income,
    earnings=MoneyInterval("per_month", pennies=2200),
    self_employment_drawings=MoneyInterval("per_month", pennies=0),
    benefits=MoneyInterval("per_month", pennies=0),
    tax_credits=MoneyInterval("per_month", pennies=0),
    child_benefits=MoneyInterval("per_month", pennies=0),
    maintenance_received=MoneyInterval("per_month", pennies=0),
    pension=MoneyInterval("per_month", pennies=0),
    other_income=MoneyInterval("per_week", pennies=2200),
)
savings = Recipe(Savings)
deductions = Recipe(
    Deductions,
    income_tax=MoneyInterval("per_week", pennies=2200),
    national_insurance=MoneyInterval("per_4week", pennies=2200),
    maintenance=MoneyInterval("per_year", pennies=2200),
    childcare=MoneyInterval("per_week", pennies=2200),
    mortgage=MoneyInterval("per_week", pennies=2200),
    rent=MoneyInterval("per_week", pennies=2200),
)

person = Recipe(Person)
full_person = Recipe(
    Person, income=foreign_key(income), savings=foreign_key(savings), deductions=foreign_key(deductions)
)

eligibility_check = Recipe(
    EligibilityCheck,
    category=foreign_key(category),
    dependants_young=5,
    dependants_old=6,
    you=foreign_key(person),
    partner=foreign_key(person),
)

eligibility_check_yes = Recipe(
    EligibilityCheck,
    category=foreign_key(category),
    dependants_young=5,
    dependants_old=6,
    you=foreign_key(person),
    partner=foreign_key(person),
    state="yes",
)

property = Recipe(Property, eligibility_check=foreign_key(eligibility_check))

personal_details = Recipe(
    PersonalDetails,
    mobile_phone=seq(555),
    home_phone=seq(7777),
    title="Dr",
    street=seq("Street"),
    postcode=seq("postcode"),
    full_name=seq("fullname"),
)

thirdparty_details = Recipe(ThirdPartyDetails, personal_details=foreign_key(personal_details))

adaptation_details = Recipe(AdaptationDetails)

matter_type1 = Recipe(MatterType, level=1)
matter_type2 = Recipe(MatterType, level=2)

media_code_group = Recipe(MediaCodeGroup)

media_code = Recipe(MediaCode, group=foreign_key(media_code_group))

empty_case = Recipe(Case)
case = Recipe(
    Case,
    eligibility_check=foreign_key(eligibility_check),
    personal_details=foreign_key(personal_details),
    media_code=foreign_key(media_code),
)

eligible_case = Recipe(
    Case,
    eligibility_check=foreign_key(eligibility_check_yes),
    diagnosis=foreign_key(diagnosis_yes),
    personal_details=foreign_key(personal_details),
    media_code=foreign_key(media_code),
)

notes_history = Recipe(CaseNotesHistory)

eod_details = Recipe(EODDetails, case=foreign_key(case))
eod_details_category = Recipe(EODDetailsCategory, eod_details=foreign_key(eod_details))
