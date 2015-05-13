# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.mail.backends import smtp


class TimeoutEmailBackend(smtp.EmailBackend):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('timeout', settings.EMAIL_TIMEOUT)
        super(TimeoutEmailBackend, self).__init__(*args, **kwargs)
