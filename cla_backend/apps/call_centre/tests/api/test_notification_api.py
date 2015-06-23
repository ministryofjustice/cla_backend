# -*- coding: utf-8 -*-
from rest_framework.test import APITestCase

from legalaid.tests.views.test_base import CLAOperatorAuthBaseApiTestMixin
from notifications.tests.views.mixins.notification_api import \
    NotificationAPIMixin


class NotificationApiTestCase(
    CLAOperatorAuthBaseApiTestMixin,
    NotificationAPIMixin,
    APITestCase
):
    pass

