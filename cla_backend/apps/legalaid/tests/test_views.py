from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from django.contrib.auth.models import Permission
from django.core.urlresolvers import reverse

from legalaid.views import FullCaseViewSet
from cla_backend.apps.call_centre.permissions import *
from cla_backend.urls import *
from rest_framework import routers
from legalaid.tests.views.test_base import CLAOperatorAuthBaseApiTestMixin


class FullCaseViewSetTestCase(CLAOperatorAuthBaseApiTestMixin,TestCase):
    def setUp(self):
        super(FullCaseViewSetTestCase, self).setUp()
        self.url = reverse('call_centre:case-list')

    def test_filter_queryset_for_unicode_characters_status_code_200(self):
        response = self.client.get(self.url+'?search=Mark%20O%E2%80%99Brien', HTTP_AUTHORIZATION='Bearer %s' % self.operator_manager_token)
        self.assertEqual(response.status_code, 200)

    def test_filter_queryset_for_only_ASCII_characters_status_code_200(self):
        response = self.client.get(self.url+'?search=John Smith', HTTP_AUTHORIZATION='Bearer %s' % self.operator_manager_token)
        self.assertEqual(response.status_code, 200)

