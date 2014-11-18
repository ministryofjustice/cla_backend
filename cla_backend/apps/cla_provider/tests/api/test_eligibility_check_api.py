from rest_framework.test import APITestCase
from rest_framework import status

from cla_common.constants import REQUIRES_ACTION_BY

from core.tests.mommy_utils import make_recipe
from legalaid.tests.views.test_base import CLAProviderAuthBaseApiTestMixin

from legalaid.tests.views.mixins.eligibility_check_api import \
    NestedEligibilityCheckAPIMixin


class EligibilityCheckTestCase(
    CLAProviderAuthBaseApiTestMixin, NestedEligibilityCheckAPIMixin,
    APITestCase
):
    LOOKUP_KEY = 'case_reference'

    @property
    def response_keys(self):
        return [
            'reference',
            'category',
            'notes',
            'your_problem_notes',
            'property_set',
            'dependants_young',
            'dependants_old',
            'you',
            'partner',
            'disputed_savings',
            'has_partner',
            'on_passported_benefits',
            'on_nass_benefits',
            'is_you_or_your_partner_over_60',
            'state',
            'specific_benefits'
        ]

    def make_parent_resource(self, **kwargs):
        kwargs.update({
            'provider': self.provider,
            'requires_action_by': REQUIRES_ACTION_BY.PROVIDER
        })
        return super(EligibilityCheckTestCase, self).make_parent_resource(
            **kwargs
        )

    def test_methods_not_allowed(self):
        super(EligibilityCheckTestCase, self).test_methods_not_allowed()

        check_without_ec = make_recipe('legalaid.case')
        list_url = self.get_detail_url(check_without_ec.reference)

        # CREATE NOT ALLOWED
        self._test_post_not_allowed(list_url)

    # CREATE

    def test_create_no_data(self):
        pass

    def test_create_basic_data(self):
        pass

    def test_create_basic_data_with_extras(self):
        pass

    def test_create_then_patch_category(self):
        pass

    def test_create_with_properties(self):
        pass

    def test_create_with_more_main_properties_fails(self):
        pass

    def test_create_with_finances(self):
        pass

    def test_errors_masked_by_drf(self):
        pass

    # SECURITY

    def test_get_not_found_if_not_belonging_to_provider(self):
        check = make_recipe('legalaid.eligibility_check')
        check_case = make_recipe(
            'legalaid.case', eligibility_check=check,
            provider=None, requires_action_by=REQUIRES_ACTION_BY.OPERATOR
        )
        detail_url = self.get_detail_url(check_case.reference)

        response = self.client.get(
            detail_url, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_not_found_if_belonging_to_different_provider(self):
        other_provider = make_recipe('cla_provider.provider')

        check = make_recipe('legalaid.eligibility_check')
        check_case = make_recipe(
            'legalaid.case', eligibility_check=check,
            provider=other_provider, requires_action_by=REQUIRES_ACTION_BY.PROVIDER
        )
        detail_url = self.get_detail_url(check_case.reference)

        response = self.client.get(
            detail_url, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
