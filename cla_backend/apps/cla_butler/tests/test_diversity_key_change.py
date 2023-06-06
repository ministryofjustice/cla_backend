import os
import mock
from django.test import TestCase
from django.db.utils import InternalError
from core.tests.mommy_utils import make_recipe
from legalaid.utils import diversity
from legalaid.models import Case


class DiversityReencryptTestCase(TestCase):
    def setUp(self):
        super(DiversityReencryptTestCase, self).setUp()
        self.expected_diversity_data = {"my key": "my value"}
        case = make_recipe("legalaid.case")
        diversity.save_diversity_data(case.personal_details.pk, self.expected_diversity_data)
        self.case = Case.objects.get(pk=case.pk)

    def get__key(self, key_name):
        file_path = os.path.join(os.path.dirname(diversity.__file__), "keys", key_name)
        with open(file_path) as f:
            return f.read()

    def _test_diversity_key_change(self, case, passphrase):
        mock_keys = {
            "DIVERSITY_PRIVATE_KEY": self.get__key("diversity_dev_reencrypt_private.key"),
            "DIVERSITY_PUBLIC_KEY": self.get__key("diversity_dev_reencrypt_public.key"),
        }
        with mock.patch.dict(os.environ, mock_keys):
            diversity.reencrypt(case.personal_details.pk, self.get__key("diversity_dev_private.key"), passphrase)

    def test_diversity_key_change_incorrect_passphrase(self):
        diversity_data = diversity.load_diversity_data(self.case.personal_details.pk, "cla")
        self.assertEqual(self.expected_diversity_data, diversity_data)

        # decrypt using old key and re-encrypt using the new key BUT with WRONG passphrase for previous key
        with self.assertRaises(InternalError):
            self._test_diversity_key_change(self.case, "wrong passphrase")

    def test_diversity_key_change_correct_passphrase(self):
        diversity_data = diversity.load_diversity_data(self.case.personal_details.pk, "cla")
        self.assertEqual(self.expected_diversity_data, diversity_data)
        self._test_diversity_key_change(self.case, "cla")

    def test_diversity_reencrypt_single_record_only(self):
        case2 = make_recipe("legalaid.case")
        diversity.save_diversity_data(case2.personal_details.pk, self.expected_diversity_data)
        # reencrypt the diversity data using the new key only for new case
        self._test_diversity_key_change(case2, "cla")

        # Load the diversity data using the old key
        diversity_data = diversity.load_diversity_data(self.case.personal_details.pk, "cla")
        self.assertEqual(self.expected_diversity_data, diversity_data)
