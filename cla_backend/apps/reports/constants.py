# -*- coding: utf-8 -*-
from model_utils import Choices


EXPORT_STATUS = Choices(
    ('CREATED', 'created', 'created'),
    ('FAILED', 'failed', 'failed'),
    ('STARTED', 'started', 'started')
)
