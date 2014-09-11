import mock

from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase
from rest_framework import status

from cla_common.constants import REQUIRES_ACTION_BY

from core.tests.mommy_utils import make_recipe

from legalaid.models import Case
from legalaid.tests.views.test_base import CLAProviderAuthBaseApiTestMixin
from legalaid.tests.views.mixins.case_api import FullCaseAPIMixin, \
    BaseSearchCaseAPIMixin, BaseUpdateCaseTestCase

from cla_eventlog.models import Log
from cla_eventlog.tests.test_views import ExplicitEventCodeViewTestCaseMixin, \
    ImplicitEventCodeViewTestCaseMixin

from cla_provider.serializers import CaseSerializer
from cla_provider.forms import RejectCaseForm


class BaseCaseTestCase(
    CLAProviderAuthBaseApiTestMixin, FullCaseAPIMixin, APITestCase
):

    @property
    def response_keys(self):
        return [
            'eligibility_check', 'personal_details', 'reference',
            'created', 'modified', 'created_by',
            'provider', 'notes', 'provider_notes',
            'full_name', 'laa_reference', 'eligibility_state',
            'adaptation_details', 'requires_action_by',
            'matter_type1', 'matter_type2', 'diagnosis', 'media_code',
            'postcode', 'diagnosis_state', 'thirdparty_details',
            'exempt_user', 'exempt_user_reason', 'ecf_statement',
            'date_of_birth', 'category'
        ]

    def get_extra_search_make_recipe_kwargs(self):
        return {
            'provider': self.provider,
            'requires_action_by': REQUIRES_ACTION_BY.PROVIDER
        }

    def get_case_serializer_clazz(self):
        return CaseSerializer

    def make_resource(self, **kwargs):
        kwargs.update({
            'provider': self.provider,
            'requires_action_by': REQUIRES_ACTION_BY.PROVIDER
        })
        return super(BaseCaseTestCase, self).make_resource(
            **kwargs
        )


class CaseGeneralTestCase(BaseCaseTestCase):
    def test_methods_not_allowed(self):
        """
        Ensure that we can't POST, PUT or DELETE
        """
        ### LIST
        self._test_delete_not_allowed(self.list_url)
        self._test_post_not_allowed(self.list_url)

        # ### DETAIL
        self._test_delete_not_allowed(self.detail_url)


class SearchCaseTestCase(BaseSearchCaseAPIMixin, BaseCaseTestCase):
    # person_ref PARAM

    def test_list_with_person_ref_param(self):
        """
        Testing that if ?person_ref param is specified, it will only return
        cases for that person.
        This is different from the related call_centre test as it
        has to ignore cases not currently assigned to the provider
        """
        Case.objects.all().delete()

        pd1 = make_recipe('legalaid.personal_details')
        pd2 = make_recipe('legalaid.personal_details')
        other_provider = make_recipe('cla_provider.provider')

        obj1 = make_recipe(
            'legalaid.case', reference='ref1',
            personal_details=pd1, provider=self.provider,
            requires_action_by=REQUIRES_ACTION_BY.PROVIDER
        )
        obj2 = make_recipe(
            'legalaid.case', reference='ref2',
            personal_details=pd2, provider=self.provider,
            requires_action_by=REQUIRES_ACTION_BY.PROVIDER
        )
        obj3 = make_recipe(  # should be ignore because different provider
            'legalaid.case', reference='ref3',
            personal_details=pd1, provider=other_provider,
            requires_action_by=REQUIRES_ACTION_BY.PROVIDER
        )
        obj4 = make_recipe(  # should be ignored because of requires_action_by
            'legalaid.case', reference='ref4',
            personal_details=pd1, provider=self.provider,
            requires_action_by=REQUIRES_ACTION_BY.OPERATOR
        )
        obj5 = make_recipe(  # should be ignored because not assigned to any provider
            'legalaid.case', reference='ref5',
            personal_details=pd1, provider=None
        )

        # searching for pd1
        response = self.client.get(
            self.get_list_person_ref_url(pd1.reference), format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data['results']))
        self.assertItemsEqual(
            [c['reference'] for c in response.data['results']],
            ['ref1']
        )

        # searching for pd2 AND dashboard=1 should ignore dashboard param
        url = '%s&dashboard=1' % self.get_list_person_ref_url(pd2.reference)
        response = self.client.get(
            url, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data['results']))
        self.assertItemsEqual(
            [case['reference'] for case in response.data['results']],
            ['ref2']
        )


class UpdateCaseTestCase(BaseUpdateCaseTestCase, BaseCaseTestCase):
    def test_patch_provider_notes_allowed(self):
        """
        Test that provider can post provider notes
        """
        response = self.client.patch(
            self.detail_url, data={'provider_notes': 'abc123'},
            format='json', HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['provider_notes'], 'abc123')

    def test_patch_operator_notes_not_allowed(self):
        """
        Test that provider cannot post operator notes
        """
        response = self.client.patch(
            self.detail_url, data={'notes': 'abc123'},
            format='json', HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data['notes'], 'abc123')


class RejectCaseTestCase(ExplicitEventCodeViewTestCaseMixin, BaseCaseTestCase):
    def get_event_code(self):
        form = RejectCaseForm(case=mock.MagicMock())
        return form.fields['event_code'].choices[0][0]

    def get_url(self, reference=None):
        reference = reference or self.resource.reference
        return reverse(
            'cla_provider:case-reject', args=(),
            kwargs={'reference': reference}
        )


class AcceptCaseTestCase(ImplicitEventCodeViewTestCaseMixin, BaseCaseTestCase):
    NO_BODY_RESPONSE = False

    def get_url(self, reference=None):
        reference = reference or self.resource.reference
        return reverse(
            'cla_provider:case-accept', args=(),
            kwargs={'reference': reference}
        )


class CloseCaseTestCase(ImplicitEventCodeViewTestCaseMixin, BaseCaseTestCase):
    def get_url(self, reference=None):
        reference = reference or self.resource.reference
        return reverse(
            'cla_provider:case-close', args=(),
            kwargs={'reference': reference}
        )


class SplitCaseTestCase(ImplicitEventCodeViewTestCaseMixin, BaseCaseTestCase):
    def setUp(self):
        super(SplitCaseTestCase, self).setUp()

    def get_default_post_data(self):
        category = make_recipe('legalaid.category')
        matter_type1 = make_recipe(
            'legalaid.matter_type1', category=category
        )
        matter_type2 = make_recipe(
            'legalaid.matter_type2', category=category
        )
        return {
            'category': category.code,
            'matter_type1': matter_type1.code,
            'matter_type2': matter_type2.code,
            'internal': False
        }

    def get_url(self, reference=None):
        reference = reference or self.resource.reference
        return reverse(
            'cla_provider:case-split', args=(),
            kwargs={'reference': reference}
        )

    def test_successful(self):
        # before, no logs
        self.assertEqual(Log.objects.count(), 0)

        data = self.get_default_post_data()
        response = self.client.post(
            self.url, data=data, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        )

        if self.NO_BODY_RESPONSE:
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        else:
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        # after, log entry created
        self.assertEqual(Log.objects.count(), 2)
