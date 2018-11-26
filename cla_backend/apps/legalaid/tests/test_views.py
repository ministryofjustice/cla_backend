import unittest

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from django.contrib.auth.models import Permission

from legalaid.tests.views.test_base import CLAProviderAuthBaseApiTestMixin
from legalaid.views import FullCaseViewSet
from cla_backend.apps.call_centre.permissions import *
from cla_backend.urls import *

from rest_framework import routers


class FullCaseViewSetTestCase(CLAProviderAuthBaseApiTestMixin, TestCase):
    def setUp(self):
        super(FullCaseViewSetTestCase, self).setUp()

    def test_filter_queryset_success_200(self):
        response = self.client.get('/call_centre/api/v1/case/?search=Mark%20O%E2%80%99Brien', HTTP_AUTHORIZATION='Bearer %s' % 'operator_manager_token')
        self.assertEqual(response.status_code, 200)
