from rest_framework.test import APITestCase

from cla_common.constants import GENDERS, ETHNICITIES, RELIGIONS,\
    SEXUAL_ORIENTATIONS, DISABILITIES

from legalaid.utils import diversity
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
        # 1. NON-EXISTING DIVERSITY
        self.assertEqual(self.resource.diversity, None)

        post_data = self._diversity_post_data()
        response = self.client.post(
            self.diversity_url, data=post_data,
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )

        self.assertEqual(response.status_code, 204)

        self.resource = self.resource.__class__.objects.get(pk=self.resource.pk)
        self.assertNotEqual(self.resource.diversity, None)

        # decrypting the diversity field to check that everything is OK
        diversity_data = diversity.load_diversity_data(self.resource.pk, 'cla')
        self.assertDictEqual(diversity_data, post_data)


        # 2. SECOND TIME => VALUES OVERRIDDEN
        new_post_data = post_data.copy()
        new_post_data['religion'] = RELIGIONS.OTHER
        new_post_data['ethnicity'] = ETHNICITIES.NOT_ASKED

        response = self.client.post(
            self.diversity_url, data=new_post_data,
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )

        self.assertEqual(response.status_code, 204)

        self.resource = self.resource.__class__.objects.get(pk=self.resource.pk)
        self.assertNotEqual(self.resource.diversity, None)

        # decrypting the diversity field to check that everything is OK
        diversity_data = diversity.load_diversity_data(self.resource.pk, 'cla')
        self.assertDictEqual(diversity_data, new_post_data)
        self.assertEqual(diversity_data.values(), new_post_data.values())
        self.assertNotEqual(diversity_data.values(), post_data.values())
