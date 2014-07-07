from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import MultipleObjectsReturned

from core.tests.mommy_utils import make_recipe, make_user

from timer.models import Timer


class RunningTimerManagerTestCase(TestCase):
    def test_query_set(self):
        timer1 = make_recipe('timer.Timer', stopped=None)
        timer2 = make_recipe('timer.Timer', stopped=timezone.now())
        timer3 = make_recipe('timer.Timer', stopped=None)

        timers = Timer.running_objects.all()
        self.assertItemsEqual(timers, [timer1, timer3])

    def test_get_by_user_fails_with_multiple_timers(self):
        user = make_user()
        make_recipe(
            'timer.Timer', stopped=None, created_by=user,
            _quantity=2
        )

        self.assertRaises(
            MultipleObjectsReturned,
            Timer.running_objects.get_by_user, user
        )

    def test_get_by_user_fails_when_no_timer(self):
        user = make_user()
        make_recipe(
            'timer.Timer', stopped=timezone.now(), created_by=user
        )

        self.assertRaises(
            IndexError,
            Timer.running_objects.get_by_user,
            user
        )

    def test_get_by_user_returns_timer(self):
        user = make_user()
        timer = make_recipe(
            'timer.Timer', stopped=None, created_by=user
        )

        self.assertEqual(
            Timer.running_objects.get_by_user(user),
            timer
        )
