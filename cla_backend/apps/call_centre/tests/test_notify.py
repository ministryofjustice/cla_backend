from django.utils import timezone
from django.test import TestCase
from django.conf import settings
from core.tests.mommy_utils import make_recipe
from cla_provider.tests.test_notify import MockGovNotifyMailBox

from checker.helpers import notify_callback_created


class NotifyTestCase(MockGovNotifyMailBox, TestCase):
    def setUp(self):
        super(NotifyTestCase, self).setUp()
        third_party = make_recipe("legalaid.thirdparty_details")
        requires_action_at_10 = timezone.datetime(year=2023, month=5, day=12, hour=10, tzinfo=timezone.utc)
        requires_action_at_11 = timezone.datetime(year=2023, month=5, day=12, hour=11, tzinfo=timezone.utc)
        self.case_third_party = make_recipe(
            "legalaid.case", thirdparty_details=third_party, requires_action_at=requires_action_at_10
        )
        self.case_personal = make_recipe("legalaid.case", requires_action_at=requires_action_at_11)

    def test_notify_callback_created_contact_third_party(self):
        case_url = "https://{0}/call_centre/{1}/"
        expected_personalisation = {
            "reference": self.case_third_party.reference,
            "contact_third_party": True,
            "contact_personal": False,
            "third_party_full_name": self.case_third_party.thirdparty_details.personal_details.full_name,
            "third_party_phone": self.case_third_party.thirdparty_details.personal_details.mobile_phone,
            "personal_full_name": self.case_third_party.personal_details.full_name,
            "case_url": case_url.format(settings.FRONTEND_HOST_NAME, self.case_third_party.reference),
            "callback_time_string": self.case_third_party.callback_time_string,
        }
        notify_callback_created(self.case_third_party)
        self.assert_last_email(
            expected_email_address=settings.CALL_CENTRE_NOTIFY_EMAIL_ADDRESS,
            expected_personalisation=expected_personalisation,
            expected_template_id=settings.GOVUK_NOTIFY_TEMPLATES["CALLBACK_CREATED_THIRD_PARTY"],
        )

    def test_notify_callback_created_contact_personal(self):
        case_url = "https://{0}/call_centre/{1}/"
        expected_personalisation = {
            "reference": self.case_personal.reference,
            "contact_third_party": False,
            "contact_personal": True,
            "personal_mobile_phone": self.case_personal.personal_details.mobile_phone,
            "personal_full_name": self.case_personal.personal_details.full_name,
            "case_url": case_url.format(settings.FRONTEND_HOST_NAME, self.case_personal.reference),
            "callback_time_string": self.case_personal.callback_time_string,
        }
        notify_callback_created(self.case_personal)
        self.assert_last_email(
            expected_email_address=settings.CALL_CENTRE_NOTIFY_EMAIL_ADDRESS,
            expected_personalisation=expected_personalisation,
            expected_template_id=settings.GOVUK_NOTIFY_TEMPLATES["CALLBACK_CREATED_PERSONAL"],
        )
