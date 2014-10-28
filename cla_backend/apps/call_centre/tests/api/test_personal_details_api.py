from rest_framework.test import APITestCase

from cla_common.constants import GENDERS, ETHNICITIES, RELIGIONS,\
    SEXUAL_ORIENTATIONS, DISABILITIES

from legalaid.tests.views.test_base import CLAOperatorAuthBaseApiTestMixin

from legalaid.tests.views.mixins.personal_details_api import \
    PersonalDetailsAPIMixin


class PersonalDetailsTestCase(
    CLAOperatorAuthBaseApiTestMixin, PersonalDetailsAPIMixin, APITestCase
):

    @property
    def diversity_url(self):
        return self.get_detail_url(self.resource_lookup_value, suffix='set-diversity')

    def _diversity_post_data(self, **kwargs):
        defaults = {
            'gender': GENDERS.PNS,
            'religion': RELIGIONS.PNS,
            'disability': DISABILITIES.PNS,
            'ethnicity': ETHNICITIES.PNS,
            'sexual_orientation': SEXUAL_ORIENTATIONS.PNS
        }

        defaults.update(kwargs)
        return defaults

    def test_set_diversity_validation(self):
        # 1. empty data
        response = self.client.post(
            self.diversity_url, data={},
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            response.data, {
                'gender': [u'This field is required.'],
                'religion': [u'This field is required.'],
                'disability': [u'This field is required.'],
                'ethnicity': [u'This field is required.'],
                'sexual_orientation': [u'This field is required.']
            }
        )

        # 2. invalid options
        response = self.client.post(
            self.diversity_url, data={
                'gender': 'invalid',
                'religion': 'invalid',
                'disability': 'invalid',
                'ethnicity': 'invalid',
                'sexual_orientation': 'invalid'
            },
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            response.data, {
                'gender': [u'Select a valid choice. invalid is not one of the available choices.'],
                'religion': [u'Select a valid choice. invalid is not one of the available choices.'],
                'disability': [u'Select a valid choice. invalid is not one of the available choices.'],
                'ethnicity': [u'Select a valid choice. invalid is not one of the available choices.'],
                'sexual_orientation': [u'Select a valid choice. invalid is not one of the available choices.']
            }
        )

    def test_set_diversity_successful(self):
        response = self.client.post(
            self.diversity_url, data=self._diversity_post_data(),
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )

        self.assertEqual(response.status_code, 200)
