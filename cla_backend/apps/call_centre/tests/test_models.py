from django.test import TestCase

from core.tests.mommy_utils import make_recipe
from call_centre.models import OP_MANAGER_GROUP_NAME, CLA_SUPERUSER_GROUP_NAME


class OperatorTestCase(TestCase):
    def test_save_sets_is_manager_True_if_is_cla_superuser_True(self):
        operator = make_recipe("call_centre.operator", is_cla_superuser=True, is_manager=False)

        self.assertTrue(operator.is_cla_superuser)
        self.assertTrue(operator.is_manager)

        # setting again is_manager to False but keeping is_cla_superuser True
        #   => is_manager should still be True

        operator.is_manager = False
        operator.save()

        self.assertTrue(operator.is_manager)

    def test_save_sets_is_staff_True_if_is_manager_or_is_cla_superuser_True(self):
        # is_manager = True
        operator = make_recipe("call_centre.operator", is_manager=True, user__is_staff=False)

        self.assertTrue(operator.is_manager)
        self.assertTrue(operator.user.is_staff)

        # setting again user.is_staff to False but keeping is_manager True
        #   => user.is_staff should still be True

        operator.user.is_staff = False
        operator.user.save()
        operator.save()

        self.assertTrue(operator.user.is_staff)

        # is_cla_superuser = True
        operator = make_recipe("call_centre.operator", is_cla_superuser=True, user__is_staff=False)

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
        operator = make_recipe("call_centre.operator", is_cla_superuser=False, is_manager=False, user__is_staff=True)

        self.assertFalse(operator.is_cla_superuser)
        self.assertFalse(operator.is_manager)
        self.assertFalse(operator.user.is_staff)

        # setting again user.is_staff to True
        #   => user.is_staff should still become False

        operator.user.is_staff = True
        operator.user.save()
        operator.save()

        self.assertFalse(operator.user.is_staff)

    def test_save_sets_groups_accordingly(self):
        # 1.
        # is_manager = False
        # is_cla_superuser = False
        #       => No groups
        operator = make_recipe("call_centre.operator", is_cla_superuser=False, is_manager=False)

        operator.save()
        self.assertEqual(operator.user.groups.count(), 0)

        # 2.
        # is_manager = True
        # is_cla_superuser = False
        #       => only OP_MANAGER_GROUP_NAME
        operator.is_manager = True
        operator.is_cla_superuser = False
        operator.save()
        self.assertEqual(operator.user.groups.count(), 1)
        self.assertEqual(operator.user.groups.filter(name=OP_MANAGER_GROUP_NAME).count(), 1)

        # 3.
        # is_manager = True
        # is_cla_superuser = True
        #       => OP_MANAGER_GROUP_NAME, CLA_SUPERUSER_GROUP_NAME
        operator.is_manager = True
        operator.is_cla_superuser = True
        operator.save()
        self.assertEqual(operator.user.groups.count(), 2)
        self.assertEqual(operator.user.groups.filter(name=OP_MANAGER_GROUP_NAME).count(), 1)
        self.assertEqual(operator.user.groups.filter(name=CLA_SUPERUSER_GROUP_NAME).count(), 1)

        # 4. back to
        # is_manager = True
        # is_cla_superuser = False
        #       => only OP_MANAGER_GROUP_NAME
        operator.is_manager = True
        operator.is_cla_superuser = False
        operator.save()
        self.assertEqual(operator.user.groups.count(), 1)
        self.assertEqual(operator.user.groups.filter(name=OP_MANAGER_GROUP_NAME).count(), 1)

        # 5. back to
        # is_manager = False
        # is_cla_superuser = False
        #       => No groups
        operator.is_manager = False
        operator.is_cla_superuser = False
        operator.save()
        self.assertEqual(operator.user.groups.count(), 0)

    def test_operator_with_organisation(self):
        organisation = make_recipe("call_centre.organisation", name="Test organisation")
        operator = make_recipe(
            "call_centre.operator", is_cla_superuser=False, is_manager=False, organisation=organisation
        )

        self.assertEqual(operator.organisation.name, "Test organisation")
        self.assertEqual(operator.organisation.id, organisation.id)
