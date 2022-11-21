import datetime
import os

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager


class SessionSecuritySeleniumTestCase(StaticLiveServerTestCase):
    """Integration tests to check the session security package is
    working as expected.
    """

    # These settings are made intentionally short in the circle CI settings file
    # (5/10s respectively).
    WARN_AFTER_SECONDS = settings.SESSION_SECURITY_WARN_AFTER
    EXPIRE_AFTER_SECONDS = settings.SESSION_SECURITY_EXPIRE_AFTER

    WAIT = 5
    TOLERANCE = 2
    TEST_LOGIN_CREDS = "test"
    TEST_SERVER = "localhost:5000"

    @classmethod
    def setUpClass(cls):
        cls.start_test_broswer()
        os.environ['DJANGO_LIVE_TEST_SERVER_ADDRESS'] = cls.TEST_SERVER
        super(StaticLiveServerTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super(StaticLiveServerTestCase, cls).tearDownClass()

    @classmethod
    def start_test_broswer(cls):
        """Starts up a headless firefox broswer for testing.
        """
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        cls.browser = webdriver.Firefox(executable_path=GeckoDriverManager().install(), options=options)

    def setUp(self):
        super(SessionSecuritySeleniumTestCase, self).setUp()
        self.setup_admin_user()

    def test_inactivity_session_timeout_procedure(self):
        """Tests that the session secuirty procedure works correctly by warning the user
        after a period of inactivity, then closing the session if there is no activity within a
        further time period.
        """
        self.login()

        # Check the session warning message is hidden and then displayed after the
        # SESSION_SECURITY_WARN_AFTER period.
        self.check_session_warning_displayed()

        # Perform activity in the browser and confirm the warning message is removed.
        self.perform_keyboard_action()
        self.assert_warning_is_hidden()

        # Check the session warning message is hidden and then displayed for a second time
        # after the SESSION_SECURITY_WARN_AFTER period.
        self.check_session_warning_displayed()

        # Check that the session is logged out after the SESSION_SECURITY_EXPIRE_AFTER period
        # when no activity is detected.
        start = datetime.datetime.now()

        expected_time_to_log_out = self.EXPIRE_AFTER_SECONDS - self.WARN_AFTER_SECONDS
        self.assert_logged_out(expected_time_to_log_out + self.TOLERANCE)

        end = datetime.datetime.now()
        delta = end - start

        self.assertGreaterEqual(delta.seconds, expected_time_to_log_out - self.TOLERANCE)

    def test_session_ends_on_browser_close(self):
        """Tests that the session is ended when the broswer is closed.
        """
        # Login to the system and then close the broswer
        self.login()
        self.browser.close()

        # Confirm that on reopening the browser and admin page that the session is
        # not restored.
        self.start_test_broswer()
        self.navigate_to_admin_page()
        self.assert_logged_out(self.WAIT)

    def check_session_warning_displayed(self):
        """Checks that the session security modal goes from hidden to visible within the
        required timeframe.
        """
        start = datetime.datetime.now()

        self.assert_warning_is_hidden()
        self.assert_warning_element_visible(self.WARN_AFTER_SECONDS + self.TOLERANCE)

        end = datetime.datetime.now()
        delta = end - start

        self.assertGreaterEqual(delta.seconds, self.WARN_AFTER_SECONDS)
        self.assertLessEqual(delta.seconds, self.EXPIRE_AFTER_SECONDS)

    def setup_admin_user(self):
        """Creates a test user for the admin portal.
        """
        ContentType.objects.clear_cache()

        if not User.objects.filter(username=self.TEST_LOGIN_CREDS).exists():
            test_user = User.objects.create(username=self.TEST_LOGIN_CREDS)
            test_user.set_password(self.TEST_LOGIN_CREDS)
            test_user.is_staff = True
            test_user.save()

    def login(self):
        """Performs admin portal login and confirms the presence of the session cookie.
        """
        self.navigate_to_admin_page()
        self.browser.find_element("id", "id_username").send_keys(self.TEST_LOGIN_CREDS)
        self.browser.find_element("id", "id_password").send_keys(self.TEST_LOGIN_CREDS)
        self.browser.find_element_by_xpath('//input[@value="Log in"]').click()
        self.confirm_logged_in()

    def navigate_to_admin_page(self):
        """Navigates to the admin portal.
        """
        self.browser.get('%s%s' % (self.live_server_url, '/admin/'))

    def perform_keyboard_action(self):
        """Simulates a user pressing the space bar within the browser.
        """
        action = ActionChains(self.browser)
        action.key_down(Keys.SPACE)
        action.key_up(Keys.SPACE)
        action.perform()

    def confirm_logged_in(self):
        """Confirms the broswers is logged into the admin portal by check for the logout button
        and the session cookie.
        """
        try:
            WebDriverWait(self.browser, self.WAIT).until(
                expected_conditions.presence_of_element_located((By.LINK_TEXT, "Log out")))
        except Exception:
            self.fail("Login was unsuccessful")

        self.assertIsNotNone(self.get_session_cookie(), "Session cookie not present after logging in.")

    def assert_warning_element_visible(self, max_wait):
        """Checks that the session security modal is visible within a given time period.

        Args:
            max_wait (float): The number fo second to wait for the element to appear.
        """
        try:
            WebDriverWait(self.browser, max_wait).until(
                expected_conditions.visibility_of_element_located((By.ID, "session_security_warning")))
        except Exception:
            self.fail("Warning message not displayed after %ds or inactivity" % (max_wait))

    def assert_warning_is_hidden(self):
        """Checks that the session security modal is non visible.
        """
        try:
            WebDriverWait(self.browser, self.WAIT).until(
                expected_conditions.invisibility_of_element((By.ID, "session_security_warning")))
        except Exception:
            self.fail("Warning message present during active session")

    def assert_logged_out(self, delay):
        """Checks that the session has been logged out by checking for the presence of the
        login page and that the session cookie has been removed.

        Args:
            delay (float): The number of second to wait for the logout to occur.
        """
        try:
            WebDriverWait(self.browser, delay).until(
                expected_conditions.presence_of_element_located((By.ID, "id_password")))
        except Exception:
            self.fail("Sessions was not logged out after %ds" % (delay))

        self.assertIsNone(self.get_session_cookie(), "Session cookie present after logging out.")

    def get_session_cookie(self):
        """Gets the session cookie from the broswer.

        Returns:
            dict: The session cookie dictionary.
        """
        cookies = (cookie for cookie in self.browser.get_cookies() if cookie["name"] == "sessionid")
        return next(cookies, None)
