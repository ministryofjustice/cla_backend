import mock
from django.test import TestCase
from django.core import management
from cla_butler.tests.mixins import CreateSampleDiversityData
from cla_butler.management.commands.diversity_data_reencrypt import Command as ClaButlerDiversityReencryptCommand
from cla_butler.models import DiversityDataCheck, ACTION, STATUS


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


class DiversityReencryptCommandTestCase(CreateSampleDiversityData, TestCase):
    def setUp(self):
        super(DiversityReencryptCommandTestCase, self).setUp()
        self.scheduled_tasks = []
        self.expected_tasks_count = 0

    def mock_schedule_tasks(self, tasks, passphrase_old, **kwargs):
        self.scheduled_tasks = tasks
        # (count divided by chunk size) plus (count mod chunk size) - Required for when you have a count that is not
        # divisible by the chunk size
        tasks_count = (len(self.pd_records_ids) / ClaButlerDiversityReencryptCommand.chunk_size) + (
            len(self.pd_records_ids) % ClaButlerDiversityReencryptCommand.chunk_size
        )
        self.assertEqual(len(tasks), tasks_count)

    @mock.patch(
        "cla_butler.management.commands.diversity_data_reencrypt.Command.get_old_key_passphrase", return_value="cla"
    )
    @mock.patch("cla_butler.management.commands.diversity_data_reencrypt.Command.schedule_tasks")
    @mock.patch.dict("os.environ", {"PREVIOUS_DIVERSITY_PRIVATE_KEY": "I am not empty"})
    def test_create_tasks_all(self, mock_schedule_tasks, get_old_key_passphrase):
        ClaButlerDiversityReencryptCommand.chunk_size = 2

        mock_schedule_tasks.side_effect = self.mock_schedule_tasks
        management.call_command("diversity_data_reencrypt")
        self.assertTrue(mock_schedule_tasks.called)

    @mock.patch(
        "cla_butler.management.commands.diversity_data_reencrypt.Command.get_old_key_passphrase", return_value="cla"
    )
    @mock.patch("cla_butler.management.commands.diversity_data_reencrypt.Command.schedule_tasks")
    @mock.patch.dict("os.environ", {"PREVIOUS_DIVERSITY_PRIVATE_KEY": "I am not empty"})
    def test_create_tasks_some(self, mock_schedule_tasks, get_old_key_passphrase):
        ClaButlerDiversityReencryptCommand.chunk_size = 2
        # Mark the first record as processed so that we can test that diversity_data_reencrypt process
        # does not attempt to reencrypt this record
        DiversityDataCheck.objects.create(
            personal_details_id=self.pd_records_ids[0], action=ACTION.REENCRYPT, status=STATUS.OK
        )

        mock_schedule_tasks.side_effect = self.mock_schedule_tasks
        management.call_command("diversity_data_reencrypt")
        self.assertTrue(mock_schedule_tasks.called)
        # Make sure that the first record is not included
        for task in self.scheduled_tasks:
            self.assertNotIn(self.pd_records_ids[0], task)
