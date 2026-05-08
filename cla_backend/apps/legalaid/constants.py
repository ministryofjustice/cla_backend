from extended_choices import Choices

DISREGARD_SELECTION = Choices(
    # This populates the "Have you had a big payment that you do not normally get?" radio button group on cla_frontend
    # constant, db_id, friendly string
    ("YES", "yes", "Yes"),
    ("NO", "no", "No"),
    ("NOT_SURE", "not_sure", "Not sure"),
)
