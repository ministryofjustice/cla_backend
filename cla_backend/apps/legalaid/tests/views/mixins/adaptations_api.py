from django.core.urlresolvers import reverse

from rest_framework import status

from legalaid.tests.views.test_base import CLAAuthBaseApiTestMixin

from core.tests.test_base import \
    NestedSimpleResourceAPIMixin


class AdaptationsMetadataAPIMixin(CLAAuthBaseApiTestMixin):

    def test_methods_not_allowed(self):
        """
        Ensure that only OPTIONS is allowed
        """
        url = reverse('%s:adaptations-metadata-list' % self.API_URL_NAMESPACE)

        self._test_delete_not_allowed(url)
        self._test_post_not_allowed(url)
        self._test_put_not_allowed(url)
        self._test_patch_not_allowed(url)
        self._test_get_not_allowed(url)


class AdaptationsDetailsAPIMixin(NestedSimpleResourceAPIMixin):
    RESOURCE_RECIPE = 'legalaid.adaptation_details'
    API_URL_BASE_NAME = 'adaptationdetails'

    @property
    def check_keys(self):
        return [
            'reference', 'bsl_webcam', 'minicom', 'text_relay',
            'skype_webcam', 'language', 'notes', 'callback_preference'
        ]

    def _create(self, data=None, url=None):
        if not url:
            self.check_case.adaptation_details = None
            self.check_case.save()
        return super(AdaptationsDetailsAPIMixin, self)._create(data=data, url=url)

    def _get_default_post_data(self):
        return {
            'bsl_webcam': True,
            'minicom': True,
            'text_relay': True,
            'skype_webcam': True,
            'language': 'ENGLISH',
            'notes': 'my notes',
            'callback_preference': True
        }

    def _test_method_in_error(self, method, url):
        """
        Generic method called by 'create' and 'patch' to test against validation
        errors.
        """
        data = {
            "language": 'sdfsdf'
        }

        method_callable = getattr(self.client, method)
        response = method_callable(
            url, data, HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        expected_errors = {
            'language': [u'Select a valid choice. sdfsdf is not one of the available choices.']
        }

        errors = response.data
        self.assertItemsEqual(
            errors.keys(), expected_errors.keys()
        )
        self.assertItemsEqual(
            errors, expected_errors
        )

    def assertAdaptationDetailsEqual(self, data, obj):
        if data is None or obj is None:
            self.assertEqual(data, obj)
        else:
            for prop in [
                'bsl_webcam', 'minicom', 'text_relay',
                'skype_webcam', 'language', 'notes',
                'callback_preference', 'reference'
            ]:
                val = obj[prop] if isinstance(obj, dict) else getattr(obj, prop)
                self.assertEqual(unicode(val), unicode(data[prop]))

    def test_methods_not_allowed(self):
        """
        Ensure that we can't DELETE to list url
        """
        ### LIST
        if hasattr(self, 'list_url') and self.list_url:
            self._test_delete_not_allowed(self.list_url)

    def test_methods_in_error(self):
        self._test_method_in_error('patch', self.detail_url)
        self._test_method_in_error('put', self.detail_url)

    # CREATE

    def test_create_with_data(self):
        """
        check variables sent as same as those that return.
        """
        data = self._get_default_post_data()
        check = self._get_default_post_data()

        response = self._create(data=data)
        # check initial state is correct

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertCheckResponseKeys(response)

        check['reference'] = response.data['reference']
        self.assertAdaptationDetailsEqual(response.data, check)

    # GET

    def test_get(self):
        adaptation_details = self.check
        self.check_case.adaptation_details = adaptation_details
        self.check_case.save()

        response = self.client.get(
            self.detail_url,
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )

        self.assertAdaptationDetailsEqual(
            response.data, self.check_case.adaptation_details
        )
