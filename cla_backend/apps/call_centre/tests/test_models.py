from django.test import TestCase
from django.utils.unittest import skip

from core.tests.mommy_utils import make_recipe


class OperatorTestCase(TestCase):
    def test_save_sets_is_manager_True_if_is_cla_superuser_True(self):
        operator = make_recipe(
            'call_centre.operator', is_cla_superuser=True, is_manager=False
        )

        self.assertTrue(operator.is_cla_superuser)
        self.assertTrue(operator.is_manager)

        # setting again is_manager to False but keeping is_cla_superuser True
        #   => is_manager should still be True

        operator.is_manager = False
        operator.save()

        self.assertTrue(operator.is_manager)

    def test_save_sets_is_staff_True_if_is_manager_or_is_cla_superuser_True(self):
        # is_manager = True
        operator = make_recipe(
            'call_centre.operator', is_manager=True, user__is_staff=False
        )

        self.assertTrue(operator.is_manager)
        self.assertTrue(operator.user.is_staff)

        # setting again user.is_staff to False but keeping is_manager True
        #   => user.is_staff should still be True

        operator.user.is_staff = False
        operator.user.save()
        operator.save()

        self.assertTrue(operator.user.is_staff)

        # is_cla_superuser = True
        operator = make_recipe(
            'call_centre.operator', is_cla_superuser=True, user__is_staff=False
        )

        self.assertTrue(operator.is_cla_superuser)
        self.assertTrue(operator.user.is_staff)

        # setting again user.is_staff to False but keeping is_cla_superuser True
        #   => user.is_staff should still be True

        operator.user.is_staff = False
        operator.user.save()
        operator.save()

        self.assertTrue(operator.user.is_staff)

    def test_save_sets_is_staff_False_if_is_manager_and_is_cla_superuser_False(self):
        # is_manager = False , is_cla_superuser = False, is_staff = True
        #   => is_staff becomes False
        operator = make_recipe(
            'call_centre.operator', is_cla_superuser=False, is_manager=False,
            user__is_staff=True
        )

        self.assertFalse(operator.is_cla_superuser)
        self.assertFalse(operator.is_manager)
        self.assertFalse(operator.user.is_staff)

        # setting again user.is_staff to True
        #   => user.is_staff should still become False

        operator.user.is_staff = True
        operator.user.save()
        operator.save()

        self.assertFalse(operator.user.is_staff)
