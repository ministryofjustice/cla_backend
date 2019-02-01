import unittest
import mock
from moj_irat.healthchecks import registry
from status import healthchecks


class HealthChecksTestCase(unittest.TestCase):
    def test_healthcheck_is_registered(self):
        registry.load_healthchecks()
        expected_names = "check_disk"
        healthcheck_names = [healthcheck.__name__ for healthcheck in registry._registry]
        self.assertIn(expected_names, healthcheck_names)

    @mock.patch("os.statvfs")
    def test_disk_space_check_passes_when_more_than_2_percent_space_is_available(self, stat_mock):
        stat_mock.return_value.f_bavail = 3 * 1024
        stat_mock.return_value.f_blocks = 100 * 1024
        stat_mock.return_value.f_frsize = 1024

        self.assertTrue(healthchecks.check_disk())

    @mock.patch("os.statvfs")
    def test_disk_space_check_fails_when_less_than_2_percent_space_is_available(self, stat_mock):
        stat_mock.return_value.f_bavail = 2 * 1024
        stat_mock.return_value.f_blocks = 100 * 1024
        stat_mock.return_value.f_frsize = 1024

        result = healthchecks.check_disk()
        self.assertFalse(result)
