from core.tests.mommy_utils import make_recipe
from core.tests.test_base import CLAOperatorAuthBaseApiTestMixin
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class AdaptationsMetadataTestCase(CLAOperatorAuthBaseApiTestMixin, APITestCase):

    def test_methods_not_allowed(self):
        """
        Ensure that only OPTIONS is allowed
        """
        url = reverse('call_centre:adaptations-metadata-list')
        self._test_delete_not_allowed(url)
        self._test_post_not_allowed(url)
        self._test_put_not_allowed(url)
        self._test_patch_not_allowed(url)
        self._test_get_not_allowed(url)
