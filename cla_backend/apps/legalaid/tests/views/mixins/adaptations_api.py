from django.core.urlresolvers import reverse


class AdaptationsMetadataAPIMixin(object):

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
