import mock
from django.test import TestCase
from django.core import management
from cla_butler.tests.mixins import CreateSampleDiversityData


class DiversityCheckCommandTestCase(CreateSampleDiversityData, TestCase):
    @mock.patch("cla_butler.management.commands.diversity_data_check.Command.get_passphrase", return_value="cla")
    @mock.patch("cla_butler.tasks.DiversityDataCheckTask.delay")
    def test_diversity_data_check(self, mock_delay, get_passphrase):
        delay_result = {"start": None, "end": None}
        expected_delay_result = {"start": 0, "end": 1000}

        def delay(*args, **kwargs):
            passphrase, start, end, description = args
            delay_result["start"] = start
            delay_result["end"] = end

        mock_delay.side_effect = delay
        management.call_command("diversity_data_check")
        self.assertDictEqual(delay_result, expected_delay_result)
