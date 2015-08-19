import types
from django.core.urlresolvers import reverse

from rest_framework import status

from core.tests.mommy_utils import make_recipe


class CLABaseApiTestMixin(object):
    """
    Useful testing methods


    NOTE: you probably don't want to subclass it directly.
        Think if it's better to use SimpleResourceAPIMixin or NestedSimpleResourceAPIMixin
        instead.
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
    """
    You should (almost) always subclass this or the NestedSimpleResourceAPIMixin
    in your TestCase.

    Your actual TestCase should also sublass one of the legalaid.tests.views.test_base
    classes.


    Usage:

    when using it, override the config properties below (in UPPERCASE).

    your test will have:
        * self.resource ==> instance of the resource you are about to test
        * self.list_url, self.details_url ==> url to list and details
        * a bunch of extra things (look around)
    """
    LOOKUP_KEY = 'pk'
    API_URL_BASE_NAME = None
    RESOURCE_RECIPE = None

    @property
    def response_keys(self):
        return []

    @property
    def resource_lookup_value(self):
        return getattr(self.resource, self.LOOKUP_KEY)

    def assertResponseKeys(self, response, keys=None, paginated=False):
        if not keys:
            keys = self.response_keys
        if hasattr(response, 'data'):
            data = response.data
            if paginated:
                data = data['results']
            if isinstance(data, types.ListType):
                for item in data:
                    self.assertItemsEqual(item, keys)
            elif isinstance(data, types.DictType):
                self.assertItemsEqual(data.keys(), keys)
        else:
            raise ValueError(
                'Must be called with response object with a .data '
                'attribute which contains a list of dicts or a dict'
            )

    def get_list_url(self):
        return reverse(
            '%s:%s-list' % (self.API_URL_NAMESPACE, self.API_URL_BASE_NAME)
        )

    def get_detail_url(self, resource_lookup_value, suffix='detail'):
        return reverse(
            '%s:%s-%s' % (self.API_URL_NAMESPACE, self.API_URL_BASE_NAME, suffix),
            args=(), kwargs={self.LOOKUP_KEY: unicode(resource_lookup_value)}
        )

    def _create(self, data=None, url=None):
        if not data:
            data = {}
        if not url:
            url = self.get_list_url()
        return self.client.post(
            url, data=data, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )

    def _patch(self, data=None, url=None):
        if not data: data = {}
        if not url: url = self.detail_url
        return self.client.patch(
            url, data=data, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )

    def setup_resources(self):
        self.resource = self.make_resource()

    def setUp(self):
        super(SimpleResourceAPIMixin, self).setUp()
        self.setup_resources()

    @property
    def list_url(self):
        return self.get_list_url()

    @property
    def detail_url(self):
        return self.get_detail_url(self.resource_lookup_value)

    def make_resource(self, **kwargs):
        return make_recipe(self.RESOURCE_RECIPE, **kwargs)


class NestedSimpleResourceAPIMixin(SimpleResourceAPIMixin):
    """
    You should (almost) always subclass this or the SimpleResourceAPIMixin
    in your TestCase.

    Your actual TestCase should also sublass one of the
    legalaid.tests.views.test_base classes.

    Usage:

    when using it, override the config properties below (in UPPERCASE).

    your test will have:
        * self.resource ==> instance of the resource you are about to test
        * self.parent_resource ==> instance of the parent resource
        * self.list_url, self.details_url ==> url to list and details
        * a bunch of extra things (look around)
    """
    LOOKUP_KEY = None  # e.g. case_reference
    PARENT_LOOKUP_KEY = None  # e.g. reference
    PARENT_RESOURCE_RECIPE = None  # e.g. legalaid.case
    PK_FIELD = None  # e.g. eligibility_check
    ONE_TO_ONE_RESOURCE = True

    @property
    def resource_lookup_value(self):
        return getattr(self.parent_resource, self.PARENT_LOOKUP_KEY)

    def get_list_url(self):
        if self.ONE_TO_ONE_RESOURCE:
            return None

        return reverse(
            '%s:%s-list' % (self.API_URL_NAMESPACE, self.API_URL_BASE_NAME),
            args=(), kwargs={self.LOOKUP_KEY: unicode(self.resource_lookup_value)}
        )

    def get_detail_url(self, resource_lookup_value, suffix='detail'):
        if self.ONE_TO_ONE_RESOURCE:
            params = {self.LOOKUP_KEY: unicode(resource_lookup_value)}
        else:
            params = {
                self.LOOKUP_KEY: unicode(resource_lookup_value),
                self.PARENT_LOOKUP_KEY: unicode(getattr(self.resource, self.PARENT_LOOKUP_KEY))
            }

        return reverse(
            '%s:%s-%s' % (self.API_URL_NAMESPACE, self.API_URL_BASE_NAME, suffix),
            args=(), kwargs=params
        )

    def setup_resources(self):
        if self.ONE_TO_ONE_RESOURCE:
            self.resource = self.make_resource()
            self.parent_resource = self.make_parent_resource(**{
                self.PK_FIELD: self.resource
            })
        else:
            self.parent_resource = self.make_parent_resource()
            self.resource = self.make_resource(**{
                self.PK_FIELD: self.parent_resource
            })

    def make_parent_resource(self, **kwargs):
        return make_recipe(self.PARENT_RESOURCE_RECIPE, **kwargs)

    def _cleanup_before_create(self):
        if self.ONE_TO_ONE_RESOURCE:
            setattr(self.parent_resource, self.PK_FIELD, None)
            self.parent_resource.save()

    def _create(self, data=None, url=None):
        self._cleanup_before_create()
        return self.client.post(
            url or self.detail_url, data=data or {}, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
