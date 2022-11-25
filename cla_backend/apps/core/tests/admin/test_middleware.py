from mock import patch, MagicMock
import unittest

from cla_backend.apps.core.admin.middleware import ClaSessionSecurityMiddleware


@patch("django.core.urlresolvers.reverse")
@patch("session_security.middleware.SessionSecurityMiddleware.process_request", return_value=None)
class TestClaSessionSecurityMiddleware(unittest.TestCase):
    """Unit tests for the ClaSessionSecurityMiddleware class.
    """

    # This regex will match any string that start with /ignore/.
    TEST_REGEX_ONE = r"^\/ignore\/.*"
    # This regex will match any string that start with /ignore/other/.
    TEST_REGEX_TWO = r"^\/ignore\/other\/.*"
    SESSION_SECURITY_PING_URL = "/session_security/ping"

    def setUp(self):
        """Sets up the required mocks for the ClaSessionSecurityMiddleware tests.
        """
        self.test_middleware = ClaSessionSecurityMiddleware()
        self.test_middleware.PASSIVE_URL_REGEX_LIST = [self.TEST_REGEX_ONE, self.TEST_REGEX_TWO]
        self.test_request = MagicMock()

    def test_process_request_handles_passive_urls_correctly(self, session_security_mock, reverse_mock):
        """Tests that the CLA session security middleware determines whether the urls is passive and
        then correctly delegates further processing to the SessionSecurityMiddleware class if required.
        """

        test_scenarios = [
            TestScenario("/ignore/me/", False),
            TestScenario("do/not/ignore", True),
            TestScenario("", True),
            TestScenario("/ignore/other/", False),
            TestScenario(self.SESSION_SECURITY_PING_URL, False),
        ]

        for scenario in test_scenarios:
            self.test_request.path = scenario.test_url
            self.test_middleware.process_request(self.test_request)

            if scenario.mock_call_expected:
                session_security_mock.assert_called_once_with(self.test_request)
            else:
                session_security_mock.assert_not_called()

            session_security_mock.reset_mock()

    def test_middleware_handles_empty_passive_url_settings_correctly(self, session_security_mock, reverse_mock):
        """Tests that the CLA session security middleware handles the PASSIVE_URL_REGEX_LIST not being set.
        """
        reverse_mock.return_value(self.SESSION_SECURITY_PING_URL)

        self.test_request.path = "/test/"
        self.test_middleware.PASSIVE_URL_REGEX_LIST = []

        self.test_middleware.process_request(self.test_request)

        session_security_mock.assert_called_once_with(self.test_request)
        session_security_mock.reset_mock()


class TestScenario(object):

    def __init__(self, test_url, mock_call_expected):
        self.test_url = test_url
        self.mock_call_expected = mock_call_expected
