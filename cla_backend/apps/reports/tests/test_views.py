import mock

from django.utils.crypto import get_random_string
from django.test import SimpleTestCase
from django.core.urlresolvers import reverse

from core.tests.mommy_utils import make_user

from ..forms import ProviderCaseClosure


class ProviderClosureVolumeViewTestCase(SimpleTestCase):
    def setUp(self):
        super(ProviderClosureVolumeViewTestCase, self).setUp()
        self.url = reverse('reports:provider_closure_volume')

    def assertResponseRequiresLogin(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, 'admin/login.html')
        self.assertEqual(response.context_data['title'], 'Log in')

    def create_and_login_user(self, is_staff=True):
        random_username = get_random_string(length=10)
        user = make_user(is_staff=is_staff, is_active=True, username=random_username)
        user.set_password('password')
        user.save()

        logged_in = self.client.login(username=random_username, password='password')
        self.assertTrue(logged_in)

    def test_access_denied_without_logging_in(self):
        # get
        response = self.client.get(self.url)
        self.assertResponseRequiresLogin(response)

        # post
        response = self.client.post(self.url)
        self.assertResponseRequiresLogin(response)

    def test_access_denied_if_user_not_staff(self):
        self.create_and_login_user(is_staff=False)

        # get
        response = self.client.get(self.url)
        self.assertResponseRequiresLogin(response)

        # post
        response = self.client.post(self.url)
        self.assertResponseRequiresLogin(response)

    def test_get_success_if_user_is_staff(self):
        self.create_and_login_user()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)

        form = response.context['form']
        self.assertTrue('form' in response.context)
        self.assertEqual(response.context['title'], 'Provider Closure Volume')

    def test_post_success(self):
        self.create_and_login_user()

        with mock.patch('reports.views.ProviderCaseClosure') as MockedForm:
            mocked_form = MockedForm()
            mocked_form.get_headers.return_value = ['1', '2', '3']
            mocked_form.get_rows.return_value = ['row1', 'row2', 'row3']

            response = self.client.post(self.url, data={})
            self.assertEqual(response.status_code, 200)
            self.assertTrue(
                'filename="provider_closure_volume.csv"' in response.serialize_headers()
            )
