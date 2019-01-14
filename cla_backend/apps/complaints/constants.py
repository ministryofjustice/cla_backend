# coding=utf-8
from model_utils import Choices


COMPLAINT_SOURCE = Choices(("EMAIL", "email", "email"), ("PHONE", "phone", "phone"), ("LETTER", "letter", "letter"))

# days between complaint creation and closing date (whether resolved or not)
SLA_DAYS = 15

# days between complaint creation and holding letter being sent
HOLDING_LETTER_SLA_DAYS = 1
