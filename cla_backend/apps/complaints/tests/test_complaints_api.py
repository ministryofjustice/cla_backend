# -*- coding: utf-8 -*-
from cla_eventlog.models import ComplaintLog, Log
from complaints.models import Complaint
from core.tests.mommy_utils import make_recipe
from core.tests.test_base import SimpleResourceAPIMixin
from django.core.urlresolvers import NoReverseMatch
from legalaid.tests.views.test_base import CLAOperatorAuthBaseApiTestMixin, \
    CLAProviderAuthBaseApiTestMixin
from rest_framework import status
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
            'category_name',
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

    def test_create_and_event_log(self):
        complaint_count = Complaint.objects.all().count()
        eod = make_recipe('legalaid.eod_details')
        complaint_cat = make_recipe('complaints.category')
        response = self._create({
            'category': complaint_cat.pk,
            'eod': eod.pk,
            'description': 'TEST DESCRIPTION',
            'source': 'EMAIL',
            'level': 29,
            'justified': True,
            'owner': self.operator_manager.pk
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(complaint_count + 1, Complaint.objects.all().count())

        resource = Complaint.objects.get(pk=response.data['id'])

        created_log = ComplaintLog.objects.get(object_id=resource.pk)

        self.assertEqual(created_log.code, 'COMPLAINT_CREATED')

    def test_patch(self):
        response = self.client.patch(self.detail_url, {
            'description': 'TEST DESCRIPTION',
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        resource = Complaint.objects.get(pk=self.resource_lookup_value)
        self.assertEqual(resource.description, 'TEST DESCRIPTION')


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
