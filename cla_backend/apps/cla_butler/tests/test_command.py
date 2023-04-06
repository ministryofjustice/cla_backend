import mock
from django.test import TestCase
from django.core import management
from cla_butler.tests.mixins import CreateSampleDiversityData


class DiversityCheckCommandTestCase(CreateSampleDiversityData, TestCase):
    @mock.patch("cla_butler.management.commands.diversity_data_check.Command.get_passphrase", return_value="cla")
    @mock.patch("cla_butler.tasks.DiversityDataCheckTask.apply_async")
    def test_diversity_data_check(self, mock_apply_async, get_passphrase):
        apply_async_result = {"pd_ids": []}

        def apply_async(*args, **kwargs):
            passphrase, pd_ids, description = args[0]
            apply_async_result["pd_ids"] = pd_ids

        mock_apply_async.side_effect = apply_async
        management.call_command("diversity_data_check")
        self.assertEqual(apply_async_result["pd_ids"], self.pd_records_ids)


