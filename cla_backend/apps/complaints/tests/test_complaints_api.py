# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.core.urlresolvers import NoReverseMatch
from rest_framework import status
from rest_framework.test import APITestCase

from call_centre.models import Operator
from cla_eventlog.constants import LOG_LEVELS
from cla_eventlog.models import ComplaintLog
from complaints.models import Complaint
from core.tests.mommy_utils import make_recipe
from core.tests.test_base import SimpleResourceAPIMixin
from legalaid.tests.views.test_base import CLAOperatorAuthBaseApiTestMixin, \
    CLAProviderAuthBaseApiTestMixin


class ComplaintTestMixin(object):
    API_URL_BASE_NAME = 'complaints'
    RESOURCE_RECIPE = 'complaints.complaint'


class BaseComplaintTestCase(
    ComplaintTestMixin, CLAOperatorAuthBaseApiTestMixin,
    SimpleResourceAPIMixin, APITestCase,
):

    def assertSingleEventCreated(self, resource, event_code):
        created_log = ComplaintLog.objects.get(
            object_id=resource.pk, code=event_code)

        self.assertEqual(created_log.code, event_code)

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
        self.assertResponseKeys(
            response=self.client.get(
                self.detail_url,
                HTTP_AUTHORIZATION=self.get_http_authorization()))

    def test_escalate_eod(self):
        complaint_count = Complaint.objects.all().count()
        eod = make_recipe('legalaid.eod_details')
        response = self._create({
            'eod': unicode(eod.reference),
            'description': 'TEST DESCRIPTION',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Complaint.objects.all().count(), complaint_count + 1)
        resource = Complaint.objects.get(pk=response.data['id'])
        self.assertSingleEventCreated(resource, 'COMPLAINT_CREATED')

    def test_create_and_event_log(self):
        complaint_count = Complaint.objects.all().count()
        eod = make_recipe('legalaid.eod_details')
        complaint_cat = make_recipe('complaints.category')
        response = self._create({
            'category': complaint_cat.pk,
            'eod': unicode(eod.reference),
            'description': 'TEST DESCRIPTION',
            'source': 'EMAIL',
            'level': LOG_LEVELS.MODERATE,
            'justified': True,
            'owner': self.operator_manager.user.username,
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(complaint_count + 1, Complaint.objects.all().count())

        resource = Complaint.objects.get(pk=response.data['id'])
        self.assertSingleEventCreated(resource, 'COMPLAINT_CREATED')
        self.assertSingleEventCreated(resource, 'OWNER_SET')

    def test_patch(self):
        response = self._patch({
            'description': 'TEST DESCRIPTION',
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        resource = Complaint.objects.get(pk=self.resource_lookup_value)
        self.assertEqual(resource.description, 'TEST DESCRIPTION')

    def test_owner_set_on_change(self):
        mgr_user = User.objects.create_user('x', 'x@x.com', 'OnionMan77')
        Operator.objects.create(user=mgr_user, is_manager=True)

        response = self._patch({
            'owner': mgr_user.username,
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        resource = Complaint.objects.get(pk=self.resource_lookup_value)
        self.assertSingleEventCreated(resource, 'OWNER_SET')

    def test_add_events_to_complaints(self):
        codes = [
            'HOLDING_LETTER_SENT',
            'FULL_RESPONSE_SENT',
            'COMPLAINT_RESOLVED',
            'COMPLAINT_CLOSED',
        ]
        for code in codes:
            response = self._create({
                'event_code': code,
                'notes': 'x' * 10000
            }, self.event_url)

            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

            self.assertSingleEventCreated(self.resource, code)

        response = self.client.get(
            self.log_url, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 4)

    @property
    def event_url(self):
        return '%sadd_event/' % self.detail_url

    @property
    def log_url(self):
        return '%slogs/' % self.detail_url


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
