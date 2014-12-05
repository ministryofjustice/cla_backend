from django.test import TestCase
from django.utils.unittest import skip


class OperatorAdminViewTestCase(TestCase):
    def setUp(self):
        super(OperatorAdminViewTestCase, self).setUp()

    # CHANGE

    @skip('not implemented yet')
    def test_op_manager_can_change_op_managers(self):
        # go to op manager change form

        # check that is_cla_superuser checkbox is not shown

        # change details + disable is_manager flat

        # save
        pass

    @skip('not implemented yet')
    def test_op_manager_cant_change_cla_superusers(self):
        # go to cla superusers change form

        # check that get 404
        pass

    @skip('not implemented yet')
    def test_cla_superuser_can_change_cla_superusers(self):
        # go to cla superuser change form

        # check that is_cla_superuser checkbox is shown

        # change details + disable is_cla_superuser

        # save
        pass

    @skip('not implemented yet')
    def test_django_superuser_can_change_everything(self):
        # go to cla superuser change form

        # check that is_cla_superuser checkbox is shown

        # change details + disable is_cla_superuser

        # save
        pass

    # CREATE

    @skip('not implemented yet')
    def test_op_manager_can_create_op_managers(self):
        # go to op add form

        # check that is_cla_superuser checkbox is not shown

        # set is_manager to True

        # save
        pass

    @skip('not implemented yet')
    def test_cla_superuser_can_create_cla_superusers(self):
        # go to op add form

        # check that is_cla_superuser checkbox is shown

        # set is_cla_superuser to True

        # save
        pass

    @skip('not implemented yet')
    def test_django_superuser_can_create_cla_superusers(self):
        # go to op add form

        # check that is_cla_superuser checkbox is shown

        # set is_cla_superuser to True

        # save
        pass

    # RESET PASSWORD

    @skip('not implemented yet')
    def test_op_manager_can_change_op_manager_password(self):
        pass

    @skip('not implemented yet')
    def test_op_manager_cant_change_cla_superuser_password(self):
        pass

    @skip('not implemented yet')
    def test_cla_superuser_can_change_cla_superuser_password(self):
        pass

    # RESET LOCKOUT

    @skip('not implemented yet')
    def test_op_manager_can_reset_op_manager_lockout(self):
        pass

    @skip('not implemented yet')
    def test_op_manager_can_reset_cla_superuser_lockout(self):
        pass

    @skip('not implemented yet')
    def test_cla_superuser_can_reset_cla_superuser_lockout(self):
        pass
