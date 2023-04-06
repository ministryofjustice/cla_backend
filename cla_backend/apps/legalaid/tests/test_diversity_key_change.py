import os
import mock
from django.test import TestCase
from django.db.utils import InternalError
from core.tests.mommy_utils import make_recipe
from legalaid.utils import diversity
from legalaid.models import Case


class FullCaseViewSetTestCase(TestCase):
    def get__key(self, key_name):
        file_path = os.path.join(os.path.dirname(diversity.__file__), "keys", key_name)
        with open(file_path) as f:
            return f.read()

    def test_diversity_key_change(self):
        expected_diversity_data = {"my key": "my value"}
        case = make_recipe("legalaid.case")
        diversity.save_diversity_data(case.personal_details.pk, expected_diversity_data)
        case = Case.objects.get(pk=case.pk)
        diversity_data = diversity.load_diversity_data(case.personal_details.pk, "cla")
        self.assertEqual(expected_diversity_data, diversity_data)

        mock_keys = {
            "DIVERSITY_PRIVATE_KEY": self.get__key("diversity_dev_reencrypt_private.key"),
            "DIVERSITY_PUBLIC_KEY": self.get__key("diversity_dev_reencrypt_public.key"),
        }
        mocker = mock.patch.dict(os.environ, mock_keys)
        mocker.start()

        # decrypt using old key and re-encrypt using the new key BUT with WRONG passphrase for previous key
        with self.assertRaises(InternalError):
            diversity.reencrypt(self.get__key("diversity_dev_private.key"), "wrong passphrase")
        mocker.stop()
        # Confirm we can still load our diversity data
        diversity_data = diversity.load_diversity_data(case.personal_details.pk, "cla")
        self.assertEqual(expected_diversity_data, diversity_data)

        # decrypt using old key and re-encrypt using the new key BUT with CORRECT passphrase for previous key
        mocker.start()
        diversity.reencrypt(self.get__key("diversity_dev_private.key"), "cla")
        case = Case.objects.get(pk=case.pk)
        diversity_data = diversity.load_diversity_data(case.personal_details.pk, "cla")
        self.assertEqual(expected_diversity_data, diversity_data)
        mocker.stop()