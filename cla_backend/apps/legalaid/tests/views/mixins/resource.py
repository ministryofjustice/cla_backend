from core.tests.mommy_utils import make_recipe
from django.core.urlresolvers import reverse


class SimpleResourceCheckAPIMixin(object):
    LOOKUP_KEY = 'reference'
    API_NAMESPACE = None
    BASE_NAME = None
    CHECK_RECIPE = None

    def __init__(self, *args, **kwargs):
        self.API_NAMESPACE = self.API_NAMESPACE or self.API_URL_NAMESPACE
        super(SimpleResourceCheckAPIMixin, self).__init__(*args, **kwargs)

    @property
    def check_keys(self):
        return []

    @property
    def check_reference(self):
        return self.check.reference

    def assertCheckResponseKeys(self, response):
        self.assertItemsEqual(
            response.data.keys(),
            self.check_keys
        )

    def get_list_url(self):
        return reverse('%s:%s-list' % (self.API_NAMESPACE, self.BASE_NAME))

    def get_detail_url(self, check_ref, suffix='detail'):
        return reverse(
            '%s:%s-%s' % (self.API_URL_NAMESPACE, self.BASE_NAME, suffix),
            args=(), kwargs={self.LOOKUP_KEY: unicode(check_ref)}
        )

    def _create(self, data=None, url=None):
        if not data: data = {}
        if not url: url = self.get_list_url()
        self.client.post(
            url, data=data, format='json',
            HTTP_AUTHORIZATION=self.get_authorization()
        )

    def setUp(self):
        super(SimpleResourceCheckAPIMixin, self).setUp()
        list_url = self.get_list_url()
        if list_url:
            self.list_url = list_url
        self.detail_url = self.get_detail_url(self.check_reference)
        self.check = make_recipe(self.CHECK_RECIPE)


class NestedSimpleResourceCheckAPIMixin(SimpleResourceCheckAPIMixin):
    LOOKUP_KEY = 'case_reference'
    API_NAMESPACE = 'checker'

    @property
    def check_reference(self):
        return self.check_case.reference

    def get_list_url(self):
        return None

    def setUp(self):
        self.check_case = make_recipe('legalaid.case')
        super(NestedSimpleResourceCheckAPIMixin, self).setUp()

    def _create(self, data=None, url=None):
        if not url: url = self.detail_url
        if not data: data = {}
        return self.client.post(
            url, data=data, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
