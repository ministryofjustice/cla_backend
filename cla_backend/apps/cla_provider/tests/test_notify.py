import mock
from datetime import datetime
from django.test import TestCase
from django.conf import settings
from core.tests.mommy_utils import make_recipe
from govuk_notify.api import GovUkNotify

from cla_provider.helpers import notify_case_assigned, notify_case_RDSPed


class NotifyTestCase(TestCase):
    def setUp(self):
        self.email = {}
        self.case = make_recipe("legalaid.case", outcome_code="SPOR")
        self.provider = make_recipe("cla_provider.provider", email_address="test@digital.justice.gov.uk", active=True)
        self.mock_send_email = mock.patch.object(GovUkNotify, "send_email", self.send_email)
        self.mock_send_email.start()

    def tearDown(self):
        super(NotifyTestCase, self).tearDown()
        self.mock_send_email.stop()

    def send_email(self, email_address, template_id, personalisation):
        self.email["to"] = email_address
        self.email["template_id"] = template_id
        self.email["personalisation"] = personalisation

    def assert_email(self, expected_email_address, expected_template_id, expected_personalisation):
        self.assertEqual(self.email["to"], expected_email_address)
        self.assertEqual(self.email["template_id"], expected_template_id)
        self.assertDictEqual(self.email["personalisation"], expected_personalisation)

    def test_notify_case_assigned_success(self):
        template_id = "ea19f5f7-ff65-40a1-9f01-4be5deda1079"
        now = datetime.now()
        case_url = "https://{}/provider/{}/".format(settings.SITE_HOSTNAME, self.case.reference)
        personalisation = {
            "reference": self.case.reference,
            "provider": self.provider.name,
            "eligibility_check_category": self.case.eligibility_check.category.name,
            "is_SPOR": self.case.outcome_code == "SPOR",
            "time": now.strftime("%H:%M"),
            "date": now.strftime("%D"),
            "case_url": case_url,
        }
        notify_case_assigned(self.provider, self.case)
        self.assert_email(self.provider.email_address, template_id, personalisation)

    def test_notify_case_RDSPed(self):
        template_id = "3f78ce41-020f-47f9-888c-f3fe568fed22"
        now = datetime.now()
        case_url = "https://{}/provider/{}/".format(settings.SITE_HOSTNAME, self.case.reference)
        personalisation = {
            "reference": self.case.reference,
            "time": now.strftime("%H:%M"),
            "date": now.strftime("%D"),
            "case_url": case_url,
        }
        notify_case_RDSPed(self.provider, self.case)
        self.assert_email(self.provider.email_address, template_id, personalisation)
