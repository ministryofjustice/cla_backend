from cla_common.constants import REQUIRES_ACTION_BY
from core.tests.mommy_utils import make_recipe
from django.core.urlresolvers import reverse

from rest_framework import status


class ProviderExtractAPIMixin(object):
    def setUp(self):
        super(ProviderExtractAPIMixin, self).setUp()
        self.creds = {
            'chs_org': 'org123',
            'chs_user': 'test_user',
            'chs_pass': 'test_pass'
        }
        self.user.staff.chs_organisation = self.creds['chs_org']
        self.user.staff.set_chs_password(self.creds['chs_pass'])
        self.user.staff.chs_user = self.creds['chs_user']

        self.user.staff.save()

        self.case = make_recipe('legalaid.case',
                                provider=self.provider,
                                requires_action_by=REQUIRES_ACTION_BY.PROVIDER)

        self.detail_url = self.get_detail_url()


    def get_valid_post_data(self, **kwargs):
        data = {
            'CHSOrganisationID': self.creds['chs_org'],
            'CHSUserName': self.creds['chs_user'],
            'CHSPassword': self.creds['chs_pass']
        }
        data.update(kwargs)
        return data

    def get_detail_url(self):
        return reverse(
            '%s:provider-extract' % self.API_URL_NAMESPACE, args=(),
        )

    def test_methods_not_allowed(self):
        """
        Ensure that we can't POST, PUT or DELETE
        """

        ### DETAIL
        self._test_put_not_allowed(self.detail_url, data=self.get_valid_post_data())
        self._test_patch_not_allowed(self.detail_url, data=self.get_valid_post_data())


    def test_post_to_get_extract_malformed_bad_request(self):
        response = self.client.post(
            self.detail_url, data=self.get_valid_post_data()
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_with_bad_creds_not_allowed(self):
        response = self.client.post(
            self.detail_url, data=self.get_valid_post_data(CHSOrganisationID='foofoofoo')
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.post(
            self.detail_url, data=self.get_valid_post_data(CHSUserName='foofoofoo')
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.post(
            self.detail_url, data=self.get_valid_post_data(CHSPassword='foofoofoo')
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_valid_post_to_extract_allowed(self):
        response = self.client.post(
            self.detail_url, data=self.get_valid_post_data(CHSCRN=self.case.reference)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_methods_not_authorized(self):
        ### DETAIL
        self._test_patch_not_authorized(self.detail_url, token=None)
        self._test_get_not_authorized(self.detail_url, token=None)
        self._test_put_not_authorized(self.detail_url, token=None)
        self._test_delete_not_authorized(self.detail_url, token=None)
