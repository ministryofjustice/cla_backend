from django.core.urlresolvers import reverse

from rest_framework import status

from core.tests.mommy_utils import make_recipe


class CLABaseApiTestMixin(object):
    """
    Useful testing methods
    """
    API_URL_NAMESPACE = None

    def get_http_authorization(self, token=None):
        if not token:
            return ''
        return 'Bearer %s' % token

    # NOT ALLOWED SHORTCUTS

    def _test_get_not_allowed(self, url, token=None):
        response = self.client.get(
            url, HTTP_AUTHORIZATION=self.get_http_authorization(token)
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def _test_post_not_allowed(self, url, data={}, token=None):
        response = self.client.post(
            url, data,
            HTTP_AUTHORIZATION=self.get_http_authorization(token)
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def _test_put_not_allowed(self, url, data={}, token=None):
        response = self.client.put(
            url, data,
            HTTP_AUTHORIZATION=self.get_http_authorization(token)
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def _test_patch_not_allowed(self, url, data={}, token=None):
        response = self.client.patch(
            url, data,
            HTTP_AUTHORIZATION=self.get_http_authorization(token)
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def _test_delete_not_allowed(self, url, token=None):
        response = self.client.delete(
            url, HTTP_AUTHORIZATION=self.get_http_authorization(token)
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # NOT AUTHORIZED SHORTCUTS

    def _test_get_not_authorized(self, url, token=None):
        response = self.client.get(
            url, HTTP_AUTHORIZATION=self.get_http_authorization(token)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def _test_post_not_authorized(self, url, data={}, token=None):
        response = self.client.post(
            url, data, HTTP_AUTHORIZATION=self.get_http_authorization(token)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def _test_put_not_authorized(self, url, data={}, token=None):
        response = self.client.put(
            url, data,
            HTTP_AUTHORIZATION=self.get_http_authorization(token)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def _test_patch_not_authorized(self, url, data={}, token=None):
        response = self.client.patch(
            url, data,
            HTTP_AUTHORIZATION=self.get_http_authorization(token)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def _test_delete_not_authorized(self, url, token=None):
        response = self.client.delete(
            url, HTTP_AUTHORIZATION=self.get_http_authorization(token)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SimpleResourceAPIMixin(CLABaseApiTestMixin):
    LOOKUP_KEY = 'pk'
    API_URL_BASE_NAME = None
    RESOURCE_RECIPE = None

    @property
    def response_keys(self):
        return []

    @property
    def resource_lookup_value(self):
        return getattr(self.resource, self.LOOKUP_KEY)

    def assertCheckResponseKeys(self, response):
        self.assertItemsEqual(
            response.data.keys(),
            self.response_keys
        )

    def get_list_url(self):
        return reverse(
            '%s:%s-list' % (self.API_URL_NAMESPACE, self.API_URL_BASE_NAME)
        )

    def get_detail_url(self, check_ref, suffix='detail'):
        return reverse(
            '%s:%s-%s' % (self.API_URL_NAMESPACE, self.API_URL_BASE_NAME, suffix),
            args=(), kwargs={self.LOOKUP_KEY: unicode(check_ref)}
        )

    def _create(self, data=None, url=None):
        if not data: data = {}
        if not url: url = self.get_list_url()
        self.client.post(
            url, data=data,
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )

    def setUp(self):
        super(SimpleResourceAPIMixin, self).setUp()

        self.resource = self.make_resource()

        list_url = self.get_list_url()
        if list_url:
            self.list_url = list_url
        self.detail_url = self.get_detail_url(self.resource_lookup_value)

    def make_resource(self):
        return make_recipe(self.RESOURCE_RECIPE)


class NestedSimpleResourceAPIMixin(SimpleResourceAPIMixin):
    LOOKUP_KEY = 'case_reference'

    @property
    def resource_lookup_value(self):
        return self.check_case.reference

    def get_list_url(self):
        return None

    def setUp(self):
        self.check_case = make_recipe('legalaid.case')
        super(NestedSimpleResourceAPIMixin, self).setUp()

    def _create(self, data=None, url=None):
        if not url: url = self.detail_url
        if not data: data = {}
        return self.client.post(
            url, data=data, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
