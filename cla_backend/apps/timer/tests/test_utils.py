import mock

from django.test import TestCase

from core.tests.mommy_utils import make_recipe, make_user

from timer.models import Timer
from timer.utils import get_timer, create_timer, \
    get_or_create_timer, stop_timer


class GetTimerTestCase(TestCase):
    def test_fails_without_authenticated_user(self):
        user = mock.MagicMock()
        user.is_authenticated.return_value = False

        self.assertRaises(ValueError, get_timer, user)

    def test_returns_None_wihout_timer_running(self):
        user = mock.MagicMock(pk=-1)
        self.assertEqual(get_timer(user), None)

    def test_returns_timer_running(self):
        timer = make_recipe('timer.Timer')
        self.assertEqual(get_timer(timer.created_by), timer)


class CreateTimerTestCase(TestCase):
    def test_fails_with_another_timer_running(self):
        user = mock.MagicMock(pk=-1)
        self.assertRaises(ValueError, create_timer, user)

    def test_creates_timer(self):
        self.assertEqual(Timer.objects.count(), 0)
        user = make_user()
        timer = create_timer(user)

        self.assertEqual(Timer.objects.count(), 1)
        timer = Timer.objects.first()

        self.assertEqual(timer.created_by, user)


class GetOrCreateTimerTestCase(TestCase):
    def test_returns_get(self):
        timer = make_recipe('timer.Timer')
        self.assertEqual(Timer.objects.count(), 1)

        db_timer, created = get_or_create_timer(timer.created_by)

        self.assertEqual(Timer.objects.count(), 1)
        self.assertEqual(db_timer, timer)
        self.assertEqual(created, False)

    def test_returns_created(self):
        self.assertEqual(Timer.objects.count(), 0)
        user = make_user()
        timer, created = get_or_create_timer(user)

        self.assertEqual(Timer.objects.count(), 1)
        timer = Timer.objects.first()

        self.assertEqual(timer.created_by, user)
        self.assertEqual(created, True)


class StopTimerTestCase(TestCase):
    def test_fails_without_running_timer(self):
        user = mock.MagicMock(pk=-1)
        self.assertRaises(ValueError, stop_timer, user)

    def test_fails_without_log(self):
        timer = make_recipe('timer.Timer')
        self.assertEqual(timer.stopped, None)

        self.assertRaises(ValueError, stop_timer, timer.created_by)

    def test_doesnt_fail_without_log_and_cancelled(self):
        timer = make_recipe('timer.Timer')
        with self.assertRaises(ValueError):
            timer.stop()

        timer.stop(cancelled=True)

    @mock.patch('timer.utils.get_timer')
    def test_stops_timer(self, mocked_get_timer):
        user = make_user()
        stop_timer(user)

        self.assertTrue(mocked_get_timer().stop.called, True)
