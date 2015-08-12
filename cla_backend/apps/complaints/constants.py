# -*- coding: utf-8 -*-
from model_utils import Choices


COMPLAINT_SOURCE = Choices(
    ('EMAIL', 'email', 'email'),
    ('PHONE', 'phone', 'phone'),
    ('LETTER', 'letter', 'letter'),
)
