import mock
from datetime import datetime
from django.test import TestCase
from django.conf import settings
from core.tests.mommy_utils import make_recipe
from govuk_notify.api import GovUkNotify

from cla_provider.helpers import notify_case_assigned, notify_case_RDSPed


class MockGovNotifyMailBox(object):
    def setUp(self):
        super(MockGovNotifyMailBox, self).setUp()
        self.mailbox = []
        self.mock_send_email = mock.patch.object(GovUkNotify, "send_email", self.send_email)
        self.mock_send_email.start()

    def tearDown(self):
        super(MockGovNotifyMailBox, self).tearDown()
        self.mock_send_email.stop()

    def send_email(self, email_address, template_id, personalisation):
        self.mailbox.append({"to": email_address, "template_id": template_id, "personalisation": personalisation})

    def assert_last_email(self, expected_email_address, expected_template_id, expected_personalisation):
        email = self.mailbox[-1]
        self.assertEqual(email["to"], expected_email_address)
        self.assertEqual(email["template_id"], expected_template_id)
        self.assertDictEqual(email["personalisation"], expected_personalisation)


class NotifyTestCase(MockGovNotifyMailBox, TestCase):
    def setUp(self):
        super(NotifyTestCase, self).setUp()
        self.case = make_recipe("legalaid.case", outcome_code="SPOR")
        self.provider = make_recipe("cla_provider.provider", email_address="test@digital.justice.gov.uk", active=True)

    def test_notify_case_assigned_success(self):
        template_id = settings.GOVUK_NOTIFY_TEMPLATES["PROVIDER_CASE_ASSIGNED"]
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
        self.assert_last_email(self.provider.email_address, template_id, personalisation)

    def test_notify_case_RDSPed(self):
        now = datetime.now()
        case_url = "https://{}/provider/{}/".format(settings.SITE_HOSTNAME, self.case.reference)
        template_id = settings.GOVUK_NOTIFY_TEMPLATES["PROVIDER_CASE_RDSP"]
        personalisation = {
            "reference": self.case.reference,
            "time": now.strftime("%H:%M"),
            "date": now.strftime("%D"),
            "case_url": case_url,
        }
        notify_case_RDSPed(self.provider, self.case)
        self.assert_last_email(self.provider.email_address, template_id, personalisation)
