from django.test import TestCase
from django.utils.unittest import skip
from django.core.urlresolvers import reverse
from django.core.management import call_command
from django.utils.crypto import get_random_string

from core.tests.mommy_utils import make_recipe, make_user

from call_centre.models import Operator, Caseworker


class OperatorAdminViewTestCase(TestCase):
    def setUp(self):
        super(OperatorAdminViewTestCase, self).setUp()

        def make_op(username, is_manager=False, is_cla_superuser=False):
            return make_recipe(
                'call_centre.operator', user__username=username,
                is_manager=is_manager,
                is_cla_superuser=is_cla_superuser
            )

        self.django_admin = make_user(is_staff=True, is_superuser=True)
        self.operators = {
            'op': make_op('op'),
            'op_manager1': make_op('op_manager1', is_manager=True),
            'op_manager2': make_op('op_manager2', is_manager=True),
            'op_superuser1': make_op('op_superuser1', is_manager=True, is_cla_superuser=True),
            'op_superuser2': make_op('op_superuser2', is_manager=True, is_cla_superuser=True),
        }

        # setting password == username
        for user in [op.user for op in self.operators.values()] + [self.django_admin]:
            user.set_password(user.username)
            user.save()

    def _reload_obj(self, obj):
        return obj.__class__.objects.get(pk=obj.pk)

    def _do_add_change_form(self, url, loggedin_op_user, should_see_is_cla_superuser, post_data):
        logged_in = self.client.login(
            username=loggedin_op_user.username,
            password=loggedin_op_user.username
        )
        self.assertTrue(logged_in)

        # go to add / change form
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        # check that is_cla_superuser checkbox is shown/not shown
        form = response.context['adminform'].form
        field_names = form.fields.keys()

        self.assertTrue('is_manager' in field_names)
        if should_see_is_cla_superuser:
            self.assertTrue('is_cla_superuser' in field_names)
        else:
            self.assertFalse('is_cla_superuser' in field_names)

        # add/change details and save
        post_response = self.client.post(url, data=post_data, follow=True)

        self.assertEqual(post_response.status_code, 200)

    def _test_change_form(self, loggedin_op_user, changing_op, should_see_is_cla_superuser, post_data):
        url = reverse('admin:call_centre_operator_change', args=(changing_op.pk,))
        self._do_add_change_form(url, loggedin_op_user, should_see_is_cla_superuser, post_data)

        # check db record
        changing_op = self._reload_obj(changing_op)
        op_user = changing_op.user
        for field in ['username', 'first_name', 'last_name']:
            self.assertEqual(getattr(op_user, field), post_data[field])
        self.assertEqual(changing_op.is_manager, post_data['is_manager'])
        self.assertEqual(
            changing_op.is_cla_superuser,
            post_data.get('is_cla_superuser', changing_op.is_cla_superuser)
        )
        self.assertEqual(
            changing_op.user.is_staff,
            changing_op.is_manager or changing_op.is_cla_superuser
        )

    def _test_add_form(self, loggedin_op_user, should_see_is_cla_superuser, post_data):
        num_operators = Operator.objects.count()

        url = reverse('admin:call_centre_operator_add')
        self._do_add_change_form(url, loggedin_op_user, should_see_is_cla_superuser, post_data)

        # check that new operator created
        self.assertEqual(Operator.objects.count(), num_operators+1)
        new_operator = Operator.objects.order_by('-created').first()

        # check db record
        op_user = new_operator.user
        for field in ['username', 'first_name', 'last_name']:
            self.assertEqual(getattr(op_user, field), post_data[field])
        self.assertEqual(new_operator.is_manager, post_data['is_manager'])
        self.assertEqual(
            new_operator.is_cla_superuser,
            post_data.get('is_cla_superuser', new_operator.is_cla_superuser)
        )
        self.assertEqual(
            new_operator.user.is_staff,
            new_operator.is_manager or new_operator.is_cla_superuser
        )

    def _test_change_password(self, loggedin_op_user, changing_op):
        logged_in = self.client.login(
            username=loggedin_op_user.username,
            password=loggedin_op_user.username
        )
        self.assertTrue(logged_in)

        # go to change password form
        change_url = reverse('admin:call_centre_operator_change', args=(changing_op.pk,))
        url = '%spassword/' % change_url
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        # change password
        post_data = {
            'password1': '123456789',
            'password2': '123456789'
        }

        # check
        post_response = self.client.post(url, data=post_data)
        self.assertRedirects(post_response, change_url)

    def _test_reset_lockout(self, loggedin_op_user, changing_op):
        logged_in = self.client.login(
            username=loggedin_op_user.username,
            password=loggedin_op_user.username
        )
        self.assertTrue(logged_in)

        # reset lockout
        change_url = reverse('admin:call_centre_operator_change', args=(changing_op.pk,))
        url = '%sreset-lockout/' % change_url
        response = self.client.post(url, follow=True)

        # check that everythin is OK
        self.assertEqual(response.status_code, 200)

    # CHANGE

    def test_op_manager_can_change_op_managers(self):
        loggedin_op = self.operators['op_manager1']
        changing_op = self.operators['op_manager2']

        # go to cla op manager2 change form
        # change changing_op.is_manager to False and save
        # check everything is OK
        post_data = {
            'username': changing_op.user.username,
            'first_name': 'New Name',
            'last_name': 'New Last Name',
            'email': 'new_email@example.com',
            'is_manager': False,
            '_save': 'Save'
        }
        self._test_change_form(
            loggedin_op.user, changing_op, should_see_is_cla_superuser=False,
            post_data=post_data
        )

    def test_op_manager_cant_change_cla_superusers(self):
        loggedin_op = self.operators['op_manager1']
        changing_op = self.operators['op_superuser1']

        # go to cla superusers change form
        logged_in = self.client.login(
            username=loggedin_op.user.username,
            password=loggedin_op.user.username
        )
        self.assertTrue(logged_in)

        # go to changing op change form
        url = reverse('admin:call_centre_operator_change', args=(changing_op.pk,))
        response = self.client.get(url)

        # check that get 404
        self.assertEqual(response.status_code, 403)

    def test_cla_superuser_can_change_cla_superusers(self):
        loggedin_op = self.operators['op_superuser1']
        changing_op = self.operators['op_superuser2']

        # go to op_superuser2 change form
        # change changing_op.is_cla_superuser to False and save
        # check everything is OK
        post_data = {
            'username': changing_op.user.username,
            'first_name': 'New Name',
            'last_name': 'New Last Name',
            'email': 'new_email@example.com',
            'is_manager': True,
            'is_cla_superuser': False,
            '_save': 'Save'
        }
        self._test_change_form(
            loggedin_op.user, changing_op, should_see_is_cla_superuser=True,
            post_data=post_data
        )

    def test_django_superuser_can_change_everything(self):
        loggedin_user = self.django_admin
        changing_op = self.operators['op_superuser2']

        # go to op_superuser2 change form
        # change changing_op.is_cla_superuser to False and save
        # check everything is OK
        post_data = {
            'username': changing_op.user.username,
            'first_name': 'New Name',
            'last_name': 'New Last Name',
            'email': 'new_email@example.com',
            'is_manager': True,
            'is_cla_superuser': False,
            '_save': 'Save'
        }
        self._test_change_form(
            loggedin_user, changing_op, should_see_is_cla_superuser=True,
            post_data=post_data
        )

    # CREATE

    def test_op_manager_can_create_op_managers(self):
        loggedin_op = self.operators['op_manager1']

        # go to op add form
        # set is_manager to True and save
        # check everything is OK
        post_data = {
            'username': get_random_string(),
            'password': '123456789',
            'password2': '123456789',
            'first_name': 'New Name',
            'last_name': 'New Last Name',
            'email': 'new_email@example.com',
            'is_manager': True,
            '_save': 'Save'
        }
        self._test_add_form(
            loggedin_op.user, should_see_is_cla_superuser=False,
            post_data=post_data
        )

    def test_cla_superuser_can_create_cla_superusers(self):
        loggedin_op = self.operators['op_superuser1']

        # go to op add form
        # set is_cla_superuser to True and save
        # check everything is OK
        post_data = {
            'username': get_random_string(),
            'password': '123456789',
            'password2': '123456789',
            'first_name': 'New Name',
            'last_name': 'New Last Name',
            'email': 'new_email@example.com',
            'is_manager': True,
            'is_cla_superuser': True,
            '_save': 'Save'
        }
        self._test_add_form(
            loggedin_op.user, should_see_is_cla_superuser=True,
            post_data=post_data
        )

    def test_django_superuser_can_create_cla_superusers(self):
        loggedin_op_user = self.django_admin

        # go to op add form
        # set is_cla_superuser to True and save
        # check everything is OK
        post_data = {
            'username': get_random_string(),
            'password': '123456789',
            'password2': '123456789',
            'first_name': 'New Name',
            'last_name': 'New Last Name',
            'email': 'new_email@example.com',
            'is_manager': True,
            'is_cla_superuser': True,
            '_save': 'Save'
        }
        self._test_add_form(
            loggedin_op_user, should_see_is_cla_superuser=True,
            post_data=post_data
        )

    # RESET PASSWORD

    def test_op_manager_can_change_op_manager_password(self):
        loggedin_op = self.operators['op_manager1']
        changing_op = self.operators['op_manager2']

        self._test_change_password(loggedin_op.user, changing_op)

    def test_op_manager_cant_change_cla_superuser_password(self):
        loggedin_op = self.operators['op_manager1']
        changing_op = self.operators['op_superuser1']

        loggedin_op_user = loggedin_op.user

        logged_in = self.client.login(
            username=loggedin_op_user.username,
            password=loggedin_op_user.username
        )
        self.assertTrue(logged_in)

        # go to change password form
        change_url = reverse('admin:call_centre_operator_change', args=(changing_op.pk,))
        url = '%spassword/' % change_url
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        # try to change password
        post_data = {
            'password1': '123456789',
            'password2': '123456789'
        }

        # check that it's not possible
        post_response = self.client.post(url, data=post_data, follow=True)
        self.assertEqual(post_response.status_code, 403)

    def test_cla_superuser_can_change_cla_superuser_password(self):
        loggedin_op = self.operators['op_superuser1']
        changing_op = self.operators['op_superuser2']

        self._test_change_password(loggedin_op.user, changing_op)

    def test_django_superuser_can_change_cla_superuser_password(self):
        loggedin_op_user = self.django_admin
        changing_op = self.operators['op_superuser2']

        self._test_change_password(loggedin_op_user, changing_op)

    # RESET LOCKOUT

    def test_op_manager_can_reset_op_manager_lockout(self):
        loggedin_op = self.operators['op_manager1']
        changing_op = self.operators['op_manager2']

        self._test_reset_lockout(loggedin_op.user, changing_op)

    def test_op_manager_cant_reset_cla_superuser_lockout(self):
        loggedin_op = self.operators['op_manager1']
        changing_op = self.operators['op_superuser1']

        loggedin_op_user = loggedin_op.user

        logged_in = self.client.login(
            username=loggedin_op_user.username,
            password=loggedin_op_user.username
        )
        self.assertTrue(logged_in)

        # try to reset lockout
        change_url = reverse('admin:call_centre_operator_change', args=(changing_op.pk,))
        url = '%sreset-lockout/' % change_url
        response = self.client.post(url, follow=True)

        # check that 403
        self.assertEqual(response.status_code, 403)

    def test_cla_superuser_can_reset_cla_superuser_lockout(self):
        loggedin_op = self.operators['op_superuser1']
        changing_op = self.operators['op_superuser2']

        self._test_reset_lockout(loggedin_op.user, changing_op)

    def test_django_superuser_can_reset_cla_superuser_lockout(self):
        loggedin_op_user = self.django_admin
        changing_op = self.operators['op_superuser2']

        self._test_reset_lockout(loggedin_op_user, changing_op)



class CaseworkerAdminViewTestCase(TestCase):
    def setUp(self):
        super(CaseworkerAdminViewTestCase, self).setUp()

        def make_op(username, is_manager=False, is_cla_superuser=False):
            return make_recipe(
                'call_centre.operator', user__username=username,
                is_manager=is_manager,
                is_cla_superuser=is_cla_superuser
            )

        def make_cw(**kwargs):
            return make_recipe('call_centre.caseworker', **kwargs)

        self.django_admin = make_user(is_staff=True, is_superuser=True)
        self.operators = {
            'op_manager1': make_op('op_manager1', is_manager=True),
            'op_superuser1': make_op('op_superuser1', is_manager=True, is_cla_superuser=True),
            'cw_1': make_cw(),
            }

        # setting password == username
        for user in [op.user for op in self.operators.values()] + [self.django_admin]:
            user.set_password(user.username)
            user.save()

    def _reload_obj(self, obj):
        return obj.__class__.objects.get(pk=obj.pk)

    def _do_add_change_form(self, url, loggedin_op_user, post_data):
        logged_in = self.client.login(
            username=loggedin_op_user.username,
            password=loggedin_op_user.username
        )
        self.assertTrue(logged_in)

        # go to add / change form
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)


        # add/change details and save
        post_response = self.client.post(url, data=post_data, follow=True)

        self.assertEqual(post_response.status_code, 200)

    def _test_change_form(self, loggedin_op_user, changing_cw, post_data):
        url = reverse('admin:call_centre_caseworker_change', args=(changing_cw.pk,))
        self._do_add_change_form(url, loggedin_op_user, post_data)

        # check db record
        changing_cw = self._reload_obj(changing_cw)
        op_user = changing_cw.user
        for field in ['username', 'first_name', 'last_name']:
            self.assertEqual(getattr(op_user, field), post_data[field])

        self.assertTrue(
            changing_cw.user.is_staff
        )

    def _test_add_form(self, loggedin_op_user, post_data):
        num_cw = Caseworker.objects.count()

        url = reverse('admin:call_centre_caseworker_add')
        self._do_add_change_form(url, loggedin_op_user, post_data)

        # check that new caseworker created
        self.assertEqual(Caseworker.objects.count(), num_cw+1)
        new_cw = Caseworker.objects.order_by('-created').first()

        # check db record
        cw_user = new_cw.user
        for field in ['username', 'first_name', 'last_name']:
            self.assertEqual(getattr(cw_user, field), post_data[field])
        self.assertTrue(
            new_cw.user.is_staff
        )

    def _test_change_password(self, loggedin_op_user, changing_cw):
        logged_in = self.client.login(
            username=loggedin_op_user.username,
            password=loggedin_op_user.username
        )
        self.assertTrue(logged_in)

        # go to change password form
        change_url = reverse('admin:call_centre_caseworker_change', args=(changing_cw.pk,))
        url = '%spassword/' % change_url
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        # change password
        post_data = {
            'password1': '123456789',
            'password2': '123456789'
        }

        # check
        post_response = self.client.post(url, data=post_data)
        self.assertRedirects(post_response, change_url)

    # CHANGE


    def test_op_manager_cant_change_laa_caseworker(self):
        loggedin_op = self.operators['op_manager1']
        changing_cw = self.operators['cw_1']

        # go to cla superusers change form
        logged_in = self.client.login(
            username=loggedin_op.user.username,
            password=loggedin_op.user.username
        )
        self.assertTrue(logged_in)

        # go to changing op change form
        url = reverse('admin:call_centre_caseworker_change', args=(changing_cw.pk,))
        response = self.client.get(url)

        # check that get 404
        self.assertEqual(response.status_code, 403)

    def test_cla_superuser_can_change_laa_caseworker(self):
        loggedin_op = self.operators['op_superuser1']
        changing_cw = self.operators['cw_1']

        # go to op_superuser2 change form
        # change changing_op.is_cla_superuser to False and save
        # check everything is OK
        post_data = {
            'username': changing_cw.user.username,
            'first_name': 'New Name',
            'last_name': 'New Last Name',
            'email': 'new_email@example.com',
            'is_staff': True,
            '_save': 'Save'
        }
        self._test_change_form(
            loggedin_op.user, changing_cw,
            post_data=post_data
        )

    def test_django_superuser_can_change_everything(self):
        loggedin_user = self.django_admin
        changing_cw = self.operators['cw_1']


        post_data = {
            'username': changing_cw.user.username,
            'first_name': 'New Name',
            'last_name': 'New Last Name',
            'email': 'new_email@example.com',
            'is_staff': True,
            '_save': 'Save'
        }
        self._test_change_form(
            loggedin_user, changing_cw,
            post_data=post_data
        )

    # CREATE


    def test_cla_superuser_can_create_cla_superusers(self):
        loggedin_op = self.operators['op_superuser1']

        # go to cw add form
        # check everything is OK
        post_data = {
            'username': get_random_string(),
            'password': '123456789',
            'password2': '123456789',
            'first_name': 'New Name',
            'last_name': 'New Last Name',
            'email': 'new_email@example.com',
            'is_staff': True,
            '_save': 'Save'
        }
        self._test_add_form(
            loggedin_op.user,
            post_data=post_data
        )

    def test_django_superuser_can_create_cla_superusers(self):
        loggedin_op_user = self.django_admin

        # go to cw add form
        # check everything is OK
        post_data = {
            'username': get_random_string(),
            'password': '123456789',
            'password2': '123456789',
            'first_name': 'New Name',
            'last_name': 'New Last Name',
            'email': 'new_email@example.com',
            'is_staff': True,
            '_save': 'Save'
        }
        self._test_add_form(
            loggedin_op_user,
            post_data=post_data
        )

    # RESET PASSWORD

    def test_op_manager_cant_change_laa_caseworker_password(self):
        loggedin_op = self.operators['op_manager1']
        changing_op = self.operators['cw_1']

        loggedin_op_user = loggedin_op.user

        logged_in = self.client.login(
            username=loggedin_op_user.username,
            password=loggedin_op_user.username
        )
        self.assertTrue(logged_in)

        # go to change password form
        change_url = reverse('admin:call_centre_caseworker_change', args=(changing_op.pk,))
        url = '%spassword/' % change_url
        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

        # try to change password
        post_data = {
            'password1': '123456789',
            'password2': '123456789'
        }

        # check that it's not possible
        post_response = self.client.post(url, data=post_data, follow=True)
        self.assertEqual(post_response.status_code, 403)

    def test_cla_superuser_can_change_cla_superuser_password(self):
        loggedin_op = self.operators['op_superuser1']
        changing_cw = self.operators['cw_1']

        self._test_change_password(loggedin_op.user, changing_cw)

    def test_django_superuser_can_change_laa_caseworker_password(self):
        loggedin_op_user = self.django_admin
        changing_cw = self.operators['cw_1']

        self._test_change_password(loggedin_op_user, changing_cw)


