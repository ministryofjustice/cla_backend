import mock
from django.test import TestCase
from django.core import management
from cla_butler.tests.mixins import CreateSampleDiversityData
from cla_butler.management.commands.diversity_reencrypt import Command as ClaButlerDiversityReencryptCommand
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
    @mock.patch(
        "cla_butler.management.commands.diversity_reencrypt.Command.get_old_key_passphrase", return_value="cla"
    )
    @mock.patch("cla_butler.management.commands.diversity_reencrypt.Command.schedule_tasks")
    @mock.patch.dict("os.environ", {"PREVIOUS_DIVERSITY_PRIVATE_KEY": "I am not empty"})
    def test_create_tasks_all(self, mock_schedule_tasks, get_old_key_passphrase):
        ClaButlerDiversityReencryptCommand.chunk_size = 2

        def schedule_tasks(tasks, passphrase_old, **kwargs):
            tasks_count = len(self.pd_records_ids) / ClaButlerDiversityReencryptCommand.chunk_size
            self.assertEqual(len(tasks), tasks_count)

        mock_schedule_tasks.side_effect = schedule_tasks
        management.call_command("diversity_reencrypt")
        self.assertTrue(mock_schedule_tasks.called)

    @mock.patch(
        "cla_butler.management.commands.diversity_reencrypt.Command.get_old_key_passphrase", return_value="cla"
    )
    @mock.patch("cla_butler.management.commands.diversity_reencrypt.Command.schedule_tasks")
    @mock.patch.dict("os.environ", {"PREVIOUS_DIVERSITY_PRIVATE_KEY": "I am not empty"})
    def test_create_tasks_some(self, mock_schedule_tasks, get_old_key_passphrase):
        ClaButlerDiversityReencryptCommand.chunk_size = 2
        # Mark the first record as processed so that we can test that diversity_reencrypt process does not attempt to
        # reencrypt this record
        DiversityDataCheck.objects.create(
            personal_details_id=self.pd_records_ids[0], action=ACTION.REENCRYPT, status=STATUS.OK
        )

        def schedule_tasks(tasks, passphrase_old, **kwargs):
            # (count divided by chunk size) plus (count mod chunk size) - Required for when you have a count that is not
            # divisible by the chunk size
            tasks_count = (len(self.pd_records_ids) / ClaButlerDiversityReencryptCommand.chunk_size) + (
                len(self.pd_records_ids) % ClaButlerDiversityReencryptCommand.chunk_size
            )
            self.assertEqual(len(tasks), tasks_count)

            # Make sure that the first record is not included
            for task in tasks:
                self.assertNotIn(self.pd_records_ids[0], task)

        mock_schedule_tasks.side_effect = schedule_tasks
        management.call_command("diversity_reencrypt")
        self.assertTrue(mock_schedule_tasks.called)
