# -*- coding: utf-8 -*-
from core.tests.test_base import SimpleResourceAPIMixin
from django.core.urlresolvers import NoReverseMatch
from legalaid.tests.views.test_base import CLAOperatorAuthBaseApiTestMixin, \
    CLAProviderAuthBaseApiTestMixin
from rest_framework.test import APITestCase


class ComplaintTestMixin(object):
    API_URL_BASE_NAME = 'complaints'
    RESOURCE_RECIPE = 'complaints.complaint'


class BaseComplaintTestCase(
    ComplaintTestMixin, CLAOperatorAuthBaseApiTestMixin,
    SimpleResourceAPIMixin, APITestCase,
):

    @property
    def response_keys(self):
        return [
            'category',
            'full_name',
            'category_of_law',
            'case_reference',
            'id',
            'created',
            'modified',
            'eod',
            'description',
            'source',
            'level',
            'justified',
            'owner',
            'created_by'
        ]

    def test_methods_not_allowed(self):
        self._test_delete_not_allowed(self.list_url)
        self._test_delete_not_allowed(self.detail_url)

    def test_response_keys(self):
        self.maxDiff = None
        self.assertResponseKeys(response=self.client.get(self.detail_url))


class BaseProviderComplaintTestCase(
    ComplaintTestMixin, CLAProviderAuthBaseApiTestMixin,
    SimpleResourceAPIMixin, APITestCase,
):
    def assertUrlsNonExistant(self, url_property_function):
        try:
            url_property_function()
            self.fail('Complaint url should not exist for providers')
        except NoReverseMatch:
            pass

    def test_methods_not_allowed(self):
        self.assertUrlsNonExistant(lambda: self.list_url)
        self.assertUrlsNonExistant(lambda: self.detail_url)
