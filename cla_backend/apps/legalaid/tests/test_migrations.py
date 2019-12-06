from django.test import TestCase
import mock

from cla_common.constants import CONTACT_SAFETY
from core.tests.mommy_utils import make_recipe
from legalaid.models import PersonalDetails
import legalaid.migrations


class NoMessageSafeToContactMigrationSetTestCase(TestCase):
    def test_migrate_no_message_to_safe_to_contact(self):
        personal_details_safe = make_recipe(
            "legalaid.personal_details", safe_to_contact=CONTACT_SAFETY.SAFE, _quantity=2
        )
        personal_details_no_call = make_recipe(
            "legalaid.personal_details", safe_to_contact=CONTACT_SAFETY.DONT_CALL, _quantity=2
        )
        personal_details_no_message = make_recipe(
            "legalaid.personal_details", safe_to_contact="NO_MESSAGE", _quantity=3
        )

        __import__("legalaid.migrations.0026_safe_to_contact_remove_no_message")
        migration = getattr(legalaid.migrations, "0026_safe_to_contact_remove_no_message")
        apps_mock = mock.Mock()
        apps_mock.get_model = mock.MagicMock(return_value=PersonalDetails)
        migration.migrate_no_message_to_safe_to_contact(apps_mock, None)

        personal_details = personal_details_safe + personal_details_no_message
        for personal_detail in personal_details:
            personal_detail = PersonalDetails.objects.get(pk=personal_detail.pk)
            self.assertEqual(personal_detail.safe_to_contact, CONTACT_SAFETY.SAFE)

        for personal_detail in personal_details_no_call:
            personal_detail = PersonalDetails.objects.get(pk=personal_detail.pk)
            self.assertEqual(personal_detail.safe_to_contact, CONTACT_SAFETY.DONT_CALL)

        self.assertEqual(PersonalDetails.objects.filter(safe_to_contact="NO_MESSAGE").count(), 0)
