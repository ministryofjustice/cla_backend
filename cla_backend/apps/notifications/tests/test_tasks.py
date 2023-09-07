import datetime
import mock
from django.test import TestCase
from django.utils import timezone
from notifications.models import Notification, Schedule, MAX_NOTIFICATION_RETRIES
from notifications.periodic_tasks import push_notifications
from core.tests.mommy_utils import make_user


class NotificationsScheduleTestCase(TestCase):
    def mock_send_notifications(self, notifications):
        self.notifications = notifications
        self.mock_send_notifications_called = True

    def setUp(self):
        self.patcher = mock.patch("notifications.periodic_tasks._send_notifications", self.mock_send_notifications)
        self.mock_send_notifications_called = False
        self.patcher.start()

    def tearDown(self):
        super(NotificationsScheduleTestCase, self).tearDown()
        self.patcher.stop()

    def test_push_notifications(self):
        now = timezone.now()
        start_time = now - datetime.timedelta(minutes=10)
        notification = Notification.objects.create(start_time=start_time, end_time=now, created_by=make_user())
        push_notifications.apply()
        self.assertTrue(self.mock_send_notifications_called)
        self.assertEqual(len(self.notifications), 1)
        schedule = Schedule.objects.get(notification=notification, is_end=False)
        self.assertTrue(schedule.completed)

    def test_push_notifications_in_the_future(self):
        now = timezone.now()
        start_time = now + datetime.timedelta(minutes=10)
        end_time = now + datetime.timedelta(minutes=20)
        Notification.objects.create(start_time=start_time, end_time=end_time, created_by=make_user())
        push_notifications.apply()
        self.assertFalse(self.mock_send_notifications_called)

    def test_push_notifications_all_completed(self):
        now = timezone.now()
        start_time = now - datetime.timedelta(minutes=10)
        end_time = now - datetime.timedelta(minutes=20)
        notification = Notification.objects.create(start_time=start_time, end_time=end_time, created_by=make_user())
        Schedule.objects.filter(notification=notification).update(completed=True)
        push_notifications.apply()
        self.assertFalse(self.mock_send_notifications_called)

    def test_push_notifications_exceeded_retries(self):
        now = timezone.now()
        start_time = now - datetime.timedelta(minutes=10)
        end_time = now - datetime.timedelta(minutes=20)
        notification = Notification.objects.create(start_time=start_time, end_time=end_time, created_by=make_user())
        Schedule.objects.filter(notification=notification).update(retried=MAX_NOTIFICATION_RETRIES)
        push_notifications.apply()
        self.assertFalse(self.mock_send_notifications_called)
