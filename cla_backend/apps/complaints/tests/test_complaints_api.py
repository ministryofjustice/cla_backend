# coding=utf-8
import datetime
import mock
import pytz

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
from legalaid.tests.views.test_base import CLAOperatorAuthBaseApiTestMixin, CLAProviderAuthBaseApiTestMixin
from django.core.urlresolvers import reverse

utc = pytz.utc


class ComplaintTestMixin(object):
    API_URL_BASE_NAME = "complaints"
    RESOURCE_RECIPE = "complaints.complaint"


class SearchComplaintTestCase(
    ComplaintTestMixin, CLAOperatorAuthBaseApiTestMixin, SimpleResourceAPIMixin, APITestCase
):
    """
    Tests to check the search functionality for complaints
    """

    API_URL_BASE_NAME = "complaints"
    RESOURCE_RECIPE = "complaints.complaint"

    @classmethod
    def setUpTestData(cls):
        cls.case_1 = make_recipe(
            "legalaid.case",
            reference="ref1",
            personal_details=make_recipe("legalaid.personal_details", full_name="abc"),
        )
        cls.case_2 = make_recipe(
            "legalaid.case",
            reference="ref2",
            personal_details=make_recipe("legalaid.personal_details", full_name="xyz"),
        )
        cls.eod_1 = make_recipe("legalaid.eod_details", notes="EOD notes 1", case=cls.case_1)
        cls.eod_2 = make_recipe("legalaid.eod_details", notes="EOD notes 2", case=cls.case_2)
        cls.complaint_cat = make_recipe("complaints.category")

    def setUp(self):
        super(CLAOperatorAuthBaseApiTestMixin, self).setUp()
        self.list_dashboard_url = u"%s?dashboard=True&page_size=20" % reverse(
            "%s:%s-list" % (self.API_URL_NAMESPACE, self.API_URL_BASE_NAME)
        )
        self.complaints = [
            self._create(
                {
                    "category": self.complaint_cat.pk,
                    "eod": unicode(self.eod_1.reference),
                    "description": "TEST DESCRIPTION",
                    "source": "EMAIL",
                    "level": LOG_LEVELS.MINOR,
                    "justified": True,
                }
            ),
            self._create(
                {
                    "category": self.complaint_cat.pk,
                    "eod": unicode(self.eod_1.reference),
                    "description": "TEST DESCRIPTION_2",
                    "source": "EMAIL",
                    "level": LOG_LEVELS.MINOR,
                    "justified": True,
                }
            ),
            self._create(
                {
                    "category": self.complaint_cat.pk,
                    "eod": unicode(self.eod_2.reference),
                    "description": "TEST DESCRIPTION_3",
                    "source": "EMAIL",
                    "level": LOG_LEVELS.MINOR,
                    "justified": True,
                }
            ),
        ]

    def test_list_with_dashboard_param(self):
        """
        Testing that list dashboard returns all results
        """
        # remove the complaint that is created by the mixin as we don't need it
        self.resource.delete()
        response = self.client.get(
            self.list_dashboard_url, HTTP_AUTHORIZATION="Bearer %s" % self.operator_manager_token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(3, len(response.data["results"]))
        self.assertEqual([case["case_reference"] for case in response.data["results"]], ["ref2", "ref1", "ref1"])

    def test_search_find_one_result_by_case_ref(self):
        """
        GET search by case reference should work
        """
        response = self.client.get(
            self.list_dashboard_url + "&search=ref2", HTTP_AUTHORIZATION="Bearer %s" % self.operator_manager_token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data["results"]))
        self.assertEqual(response.data["results"][0]["case_reference"], "ref2")

    def test_search_find_multiple_results_by_person_name(self):
        # remove the complaint that is created by the mixin as we don't need it
        self.resource.delete()

        # """
        # GET search by name should work
        # """
        response = self.client.get(
            self.list_dashboard_url + "&search=abc", HTTP_AUTHORIZATION="Bearer %s" % self.operator_manager_token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(2, len(response.data["results"]))
        self.assertEqual(response.data["results"][0]["full_name"], "abc")

    def test_search_find_zero_result_by_case_ref(self):
        """
        GET search by value that returns zero results
        """
        response = self.client.get(
            self.list_dashboard_url + "&search=ref3", HTTP_AUTHORIZATION="Bearer %s" % self.operator_manager_token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(0, len(response.data["results"]))


class ComplaintTestCase(ComplaintTestMixin, CLAOperatorAuthBaseApiTestMixin, SimpleResourceAPIMixin, APITestCase):
    def assertSingleEventCreated(self, resource, event_code):
        created_log = ComplaintLog.objects.get(object_id=resource.pk, code=event_code)

        self.assertEqual(created_log.code, event_code)

    @property
    def response_keys(self):
        return [
            "id",
            "created",
            "modified",
            "case_reference",
            "full_name",
            "category_of_law",
            "created_by",
            "eod",
            "category",
            "category_name",
            "description",
            "owner",
            "source",
            "level",
            "justified",
            "status_label",
            "resolved",
            "closed",
            "voided",
            "holding_letter",
            "full_letter",
            "out_of_sla",
            "holding_letter_out_of_sla",
            "requires_action_at",
        ]

    def test_methods_not_allowed(self):
        self._test_delete_not_allowed(self.list_url)
        self._test_delete_not_allowed(self.detail_url)

    def test_response_keys(self):
        self.maxDiff = None
        self.assertResponseKeys(
            response=self.client.get(self.detail_url, HTTP_AUTHORIZATION=self.get_http_authorization())
        )

    def test_escalate_eod(self):
        complaint_count = Complaint.objects.all().count()
        eod = make_recipe("legalaid.eod_details")
        response = self._create({"eod": unicode(eod.reference), "description": "TEST DESCRIPTION"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Complaint.objects.all().count(), complaint_count + 1)

        resource = Complaint.objects.get(pk=response.data["id"])
        self.assertEqual(resource.created_by, self.user)
        self.assertSingleEventCreated(resource, "COMPLAINT_CREATED")

    def test_create_and_event_log(self):
        complaint_count = Complaint.objects.all().count()
        eod = make_recipe("legalaid.eod_details")
        complaint_cat = make_recipe("complaints.category")
        response = self._create(
            {
                "category": complaint_cat.pk,
                "eod": unicode(eod.reference),
                "description": "TEST DESCRIPTION",
                "source": "EMAIL",
                "level": LOG_LEVELS.MINOR,
                "justified": True,
                "owner": self.operator_manager.user.username,
            }
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(complaint_count + 1, Complaint.objects.all().count())

        resource = Complaint.objects.get(pk=response.data["id"])
        self.assertSingleEventCreated(resource, "COMPLAINT_CREATED")
        self.assertSingleEventCreated(resource, "OWNER_SET")
        self.assertTrue(resource.eod.case.complaint_flag)

    def test_patch(self):
        response = self._patch({"description": "TEST DESCRIPTION"})
        self.refresh_resource()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.resource.description, "TEST DESCRIPTION")

    def test_owner_set_on_change(self):
        mgr_user = User.objects.create_user("x", "x@x.com", "OnionMan77")
        Operator.objects.create(user=mgr_user, is_manager=True)

        self.assertEqual(self.resource.status_label, "received")
        response = self._patch({"owner": mgr_user.username})
        self.refresh_resource()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertSingleEventCreated(self.resource, "OWNER_SET")
        self.assertEqual(self.resource.status_label, "pending")

    def test_add_events_to_complaints(self):
        codes = ["COMPLAINT_NOTE", "HOLDING_LETTER_SENT", "FULL_RESPONSE_SENT", "TRANSFERRED_TO_SPECIALIST"]
        for code in codes:
            response = self._create({"event_code": code, "notes": "x" * 10000}, self.event_url)
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            self.assertSingleEventCreated(self.resource, code)

        response = self.client.get(self.log_url, format="json", HTTP_AUTHORIZATION=self.get_http_authorization())
        self.refresh_resource()
        self.assertIsNotNone(self.resource.holding_letter)
        self.assertIsNotNone(self.resource.full_letter)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)
        self.assertEqual(self.resource.status_label, "received")

    def test_complaint_closing(self):
        response = self._create(
            {"event_code": "COMPLAINT_CLOSED", "notes": "closing notes", "resolved": True}, self.event_url
        )
        self.refresh_resource()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertSingleEventCreated(self.resource, "COMPLAINT_CLOSED")
        self.assertEqual(self.resource.resolved, True)
        self.assertEqual(self.resource.status_label, "resolved")
        self.assertIsNotNone(self.resource.closed)
        self.assertFalse(self.resource.eod.case.complaint_flag)

        response = self.client.get(self.log_url, format="json", HTTP_AUTHORIZATION=self.get_http_authorization())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_complaint_voiding(self):
        response = self._create({"event_code": "COMPLAINT_VOID", "notes": "compaint created in error"}, self.event_url)
        self.refresh_resource()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertSingleEventCreated(self.resource, "COMPLAINT_VOID")
        self.assertEqual(self.resource.status_label, "voided")
        self.assertFalse(self.resource.eod.case.complaint_flag)

        response = self.client.get(self.log_url, format="json", HTTP_AUTHORIZATION=self.get_http_authorization())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_complaint_reopening(self):
        self._create({"event_code": "COMPLAINT_CLOSED", "notes": "some notes", "resolved": False}, self.event_url)
        self.refresh_resource()
        self.assertSingleEventCreated(self.resource, "COMPLAINT_CLOSED")
        self.assertFalse(self.resource.eod.case.complaint_flag)

        response = self._create({}, self.reopen_url)
        self.refresh_resource()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertSingleEventCreated(self.resource, "COMPLAINT_REOPENED")
        self.assertIsNone(self.resource.resolved)
        self.assertIsNone(self.resource.closed)
        self.assertTrue(self.resource.eod.case.complaint_flag)

    def test_voided_complaint_reopening(self):
        self._create({"event_code": "COMPLAINT_VOID", "notes": "some notes"}, self.event_url)
        self.refresh_resource()
        self.assertSingleEventCreated(self.resource, "COMPLAINT_VOID")
        self.assertFalse(self.resource.eod.case.complaint_flag)

        response = self._create({}, self.reopen_url)
        self.refresh_resource()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertSingleEventCreated(self.resource, "COMPLAINT_REOPENED")
        self.assertIsNone(self.resource.resolved)
        self.assertIsNone(self.resource.closed)
        self.assertTrue(self.resource.eod.case.complaint_flag)

    def test_complaint_sla(self):
        self.assertEqual(self.resource.out_of_sla, False)
        now = datetime.datetime(2015, 9, 2, 11, 30).replace(tzinfo=utc)
        self.resource.created = now
        fourteen_days_later = datetime.datetime(2015, 9, 19, 11, 29).replace(tzinfo=utc)
        fifteen_days_later = datetime.datetime(2015, 9, 19, 11, 31).replace(tzinfo=utc)
        with mock.patch("django.utils.timezone.now") as mocked_now:
            mocked_now.return_value = fourteen_days_later
            self.assertEqual(self.resource.out_of_sla, False)
            self.assertEqual(self.resource.holding_letter_out_of_sla, True)
        with mock.patch("django.utils.timezone.now") as mocked_now:
            mocked_now.return_value = fifteen_days_later
            self.assertEqual(self.resource.out_of_sla, True)
            self.assertEqual(self.resource.holding_letter_out_of_sla, True)

    def test_days_from_sla(self):
        pass

    @property
    def log_url(self):
        return "%slogs/" % self.detail_url

    @property
    def event_url(self):
        return "%sadd_event/" % self.detail_url

    @property
    def reopen_url(self):
        return "%sreopen/" % self.detail_url


class ProviderComplaintTestCase(
    ComplaintTestMixin, CLAProviderAuthBaseApiTestMixin, SimpleResourceAPIMixin, APITestCase
):
    def assertUrlsNonExistant(self, url_property_function):
        try:
            url_property_function()
            self.fail("Complaint url should not exist for providers")
        except NoReverseMatch:
            pass

    def test_methods_not_allowed(self):
        self.assertUrlsNonExistant(lambda: self.list_url)
        self.assertUrlsNonExistant(lambda: self.detail_url)
