from rest_framework import status

from core.tests.mommy_utils import make_recipe
from core.tests.test_base import NestedSimpleResourceAPIMixin


class CaseNotesHistoryAPIMixin(NestedSimpleResourceAPIMixin):
    LOOKUP_KEY = 'reference'
    API_URL_BASE_NAME = 'casenoteshistory'
    RESOURCE_RECIPE = 'legalaid.notes_history'
    LOOKUP_KEY = 'case_reference'
    PARENT_LOOKUP_KEY = 'reference'
    PARENT_RESOURCE_RECIPE = 'legalaid.case'
    PK_FIELD = 'case'
    ONE_TO_ONE_RESOURCE = False

    def setup_resources(self):
        super(CaseNotesHistoryAPIMixin, self).setup_resources()
        self.operator_notes = make_recipe(
            self.RESOURCE_RECIPE, case=self.parent_resource,
            operator_notes='Operator notes',
            provider_notes=None,
            _quantity=4
        )
        self.provider_notes = make_recipe(
            self.RESOURCE_RECIPE, case=self.parent_resource,
            provider_notes='Provider notes',
            operator_notes=None,
            _quantity=4
        )

        # creating extra notes on different case
        extra_case = make_recipe('legalaid.case')
        make_recipe(
            self.RESOURCE_RECIPE, case=extra_case, _quantity=4
        )

    def make_resource(self, **kwargs):
        return None

    def test_methods_not_allowed(self):
        """
        Ensure that we can't POST, PUT or DELETE
        """
        self._test_post_not_allowed(self.list_url)
        self._test_put_not_allowed(self.list_url)
        self._test_delete_not_allowed(self.list_url)

    def test_methods_not_authorized(self):
        self._test_get_not_authorized(self.list_url, self.invalid_token)

    def assertResponseKeys(self, response, *kwargs):
        self.assertTrue('results' in response.data)

        results = response.data['results']
        if response.data['count'] > 0:
            self.assertItemsEqual(
                results[0].keys(),
                [
                    'created_by', 'created', 'operator_notes',
                    'provider_notes', 'type_notes'
                ]
            )

    def test_get_without_type_param(self):
        response = self.client.get(
            self.list_url, HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertResponseKeys(response)
        self.assertEqual(response.data['count'], 8)
        self.assertEqual(len(response.data['results']), 5)

        for obj in response.data['results']:
            if obj['provider_notes'] != None:
                self.assertEqual(obj['provider_notes'], 'Provider notes')
                self.assertEqual(obj['type_notes'], 'Provider notes')
            else:
                self.assertEqual(obj['operator_notes'], 'Operator notes')
                self.assertEqual(obj['type_notes'], 'Operator notes')

    def test_get_with_operator_type(self):
        url = "%s?type=operator" % self.list_url
        response = self.client.get(
            url, HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertResponseKeys(response)
        self.assertEqual(response.data['count'], 4)

        for obj in response.data['results']:
            self.assertEqual(obj['provider_notes'], None)
            self.assertEqual(obj['operator_notes'], 'Operator notes')
            self.assertEqual(obj['type_notes'], 'Operator notes')

    def test_get_with_cla_provider_type(self):
        url = "%s?type=cla_provider" % self.list_url
        response = self.client.get(
            url, HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertResponseKeys(response)
        self.assertEqual(response.data['count'], 4)

        for obj in response.data['results']:
            self.assertEqual(obj['operator_notes'], None)
            self.assertEqual(obj['provider_notes'], 'Provider notes')
            self.assertEqual(obj['type_notes'], 'Provider notes')

    def test_get_with_with_extra_param(self):
        url = "%s?with_extra=true" % self.list_url
        response = self.client.get(
            url, HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertResponseKeys(response)
        self.assertEqual(response.data['count'], 8)
        self.assertEqual(len(response.data['results']), 6)

        for obj in response.data['results']:
            if obj['provider_notes'] is not None:
                self.assertEqual(obj['provider_notes'], 'Provider notes')
                self.assertEqual(obj['type_notes'], 'Provider notes')
            else:
                self.assertEqual(obj['operator_notes'], 'Operator notes')
                self.assertEqual(obj['type_notes'], 'Operator notes')
