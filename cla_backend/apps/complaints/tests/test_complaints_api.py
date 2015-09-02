# -*- coding: utf-8 -*-
import datetime
import mock

from django.contrib.auth.models import User
from django.core.urlresolvers import NoReverseMatch
from django.utils import timezone
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


class ComplaintTestCase(
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
            'id',
            'created',
            'modified',

            'case_reference',
            'full_name',
            'category_of_law',

            'created_by',
            'eod',
            'category',
            'category_name',
            'description',
            'owner',
            'source',
            'level',
            'justified',

            'status_label',
            'resolved',
            'closed',
            'holding_letter',
            'full_letter',
            'out_of_sla',
            'holding_letter_out_of_sla',
            'requires_action_at',
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
            'level': LOG_LEVELS.MINOR,
            'justified': True,
            'owner': self.operator_manager.user.username,
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(complaint_count + 1, Complaint.objects.all().count())

        resource = Complaint.objects.get(pk=response.data['id'])
        self.assertSingleEventCreated(resource, 'COMPLAINT_CREATED')
        self.assertSingleEventCreated(resource, 'OWNER_SET')
        self.assertTrue(resource.eod.case.complaint_flag)

    def test_patch(self):
        response = self._patch({
            'description': 'TEST DESCRIPTION',
        })
        self.refresh_resource()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.resource.description, 'TEST DESCRIPTION')

    def test_owner_set_on_change(self):
        mgr_user = User.objects.create_user('x', 'x@x.com', 'OnionMan77')
        Operator.objects.create(user=mgr_user, is_manager=True)

        self.assertEqual(self.resource.status_label, 'received')
        response = self._patch({
            'owner': mgr_user.username,
        })
        self.refresh_resource()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertSingleEventCreated(self.resource, 'OWNER_SET')
        self.assertEqual(self.resource.status_label, 'pending')

    def test_add_events_to_complaints(self):
        codes = [
            'COMPLAINT_NOTE',
            'HOLDING_LETTER_SENT',
            'FULL_RESPONSE_SENT',
        ]
        for code in codes:
            response = self._create({
                'event_code': code,
                'notes': 'x' * 10000,
            }, self.event_url)
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            self.assertSingleEventCreated(self.resource, code)

        response = self.client.get(
            self.log_url, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.refresh_resource()
        self.assertIsNotNone(self.resource.holding_letter)
        self.assertIsNotNone(self.resource.full_letter)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(self.resource.status_label, 'received')

    def test_complaint_closing(self):
        response = self._create({
            'event_code': 'COMPLAINT_CLOSED',
            'notes': 'closing notes',
            'resolved': True,
        }, self.event_url)
        self.refresh_resource()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertSingleEventCreated(self.resource, 'COMPLAINT_CLOSED')
        self.assertEqual(self.resource.resolved, True)
        self.assertEqual(self.resource.status_label, 'resolved')
        self.assertIsNotNone(self.resource.closed)
        self.assertFalse(self.resource.eod.case.complaint_flag)

        response = self.client.get(
            self.log_url, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_complaint_reopening(self):
        self._create({
            'event_code': 'COMPLAINT_CLOSED',
            'notes': 'some notes',
            'resolved': False,
        }, self.event_url)
        self.refresh_resource()
        self.assertSingleEventCreated(self.resource, 'COMPLAINT_CLOSED')
        self.assertFalse(self.resource.eod.case.complaint_flag)

        response = self._create({}, self.reopen_url)
        self.refresh_resource()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertSingleEventCreated(self.resource, 'COMPLAINT_REOPENED')
        self.assertIsNone(self.resource.resolved)
        self.assertIsNone(self.resource.closed)
        self.assertTrue(self.resource.eod.case.complaint_flag)

    def test_complaint_sla(self):
        self.assertEqual(self.resource.out_of_sla, False)
        now = timezone.now()
        fourteen_days_later = now + datetime.timedelta(days=14, hours=23)
        fifteen_days_later = now + datetime.timedelta(days=15)
        with mock.patch('django.utils.timezone.now') as mocked_now:
            mocked_now.return_value = fourteen_days_later
            self.assertEqual(self.resource.out_of_sla, False)
            self.assertEqual(self.resource.holding_letter_out_of_sla, True)
        with mock.patch('django.utils.timezone.now') as mocked_now:
            mocked_now.return_value = fifteen_days_later
            self.assertEqual(self.resource.out_of_sla, True)
            self.assertEqual(self.resource.holding_letter_out_of_sla, True)

    @property
    def log_url(self):
        return '%slogs/' % self.detail_url

    @property
    def event_url(self):
        return '%sadd_event/' % self.detail_url

    @property
    def reopen_url(self):
        return '%sreopen/' % self.detail_url


class ProviderComplaintTestCase(
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
