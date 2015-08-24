import mock

from django.core.urlresolvers import reverse
from django.utils import timezone

from rest_framework.test import APITestCase
from rest_framework import status

from cla_common.constants import REQUIRES_ACTION_BY

from core.tests.mommy_utils import make_recipe

from legalaid.models import Case, CaseNotesHistory
from legalaid.tests.views.test_base import CLAProviderAuthBaseApiTestMixin
from legalaid.tests.views.mixins.case_api import BaseFullCaseAPIMixin, \
    FullCaseAPIMixin, BaseSearchCaseAPIMixin, BaseUpdateCaseTestCase

from cla_eventlog.models import Log
from cla_eventlog.tests.test_views import ExplicitEventCodeViewTestCaseMixin, \
    ImplicitEventCodeViewTestCaseMixin

from cla_provider.serializers import CaseSerializer
from cla_provider.forms import RejectCaseForm


class BaseCaseTestCase(
    CLAProviderAuthBaseApiTestMixin, BaseFullCaseAPIMixin, APITestCase
):

    @property
    def response_keys(self):
        return [
            'eligibility_check', 'personal_details', 'reference',
            'created', 'modified', 'created_by', 'outcome_code',
            'outcome_description',  'provider', 'notes', 'provider_notes',
            'provider_viewed', 'provider_accepted', 'provider_closed',
            'full_name', 'laa_reference', 'eligibility_state',
            'adaptation_details', 'requires_action_by',
            'matter_type1', 'matter_type2', 'diagnosis', 'media_code',
            'postcode', 'diagnosis_state', 'thirdparty_details',
            'exempt_user', 'exempt_user_reason', 'ecf_statement',
            'date_of_birth', 'category', 'source', 'complaint_flag'
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


class CaseGeneralTestCase(BaseCaseTestCase, FullCaseAPIMixin):
    def test_methods_not_allowed(self):
        """
        Ensure that we can't POST, PUT or DELETE
        """
        # LIST
        self._test_delete_not_allowed(self.list_url)
        self._test_post_not_allowed(self.list_url)

        # DETAIL
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
        obj4 = make_recipe(  # should be ignored because of outcome_code 'IRCB'
            'legalaid.case', reference='ref4',
            personal_details=pd1, provider=self.provider,
            outcome_code='IRCB'
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


class FilteredSearchCaseTestCase(BaseCaseTestCase):
    def setUp(self):
        """
            obj1 on operator queue => always ignored
            obj2 assigned to different provider => always ignored
            obj3 assigned to provider => new
            obj4 assigned and opened by provider => opened
            obj5 assigned to provider but marked as 'IRCB' => always ignored
            obj6 accepted by provider => accepted
            obj7 closed by provider => closed
        """
        super(FilteredSearchCaseTestCase, self).setUp()

        Case.objects.all().delete()

        other_provider = make_recipe('cla_provider.provider')

        self.cases = [
            # obj1 on operator queue => always ignored
            make_recipe(
                'legalaid.case', reference='ref1',
                provider=None
            ),

            # obj2 assigned to different provider => always ignored
            make_recipe(
                'legalaid.case', reference='ref2',
                provider=other_provider
            ),

            # obj3 assigned to provider => new
            make_recipe(
                'legalaid.case', reference='ref3',
                provider=self.provider,
                provider_viewed=None,
                provider_accepted=None,
                provider_closed=None
            ),

            # obj4 assigned and opened by provider => opened
            make_recipe(
                'legalaid.case', reference='ref4',
                provider=self.provider,
                provider_viewed=timezone.now(),
                provider_accepted=None,
                provider_closed=None
            ),

            # obj5 assigned to provider but marked as 'IRCB' => always ignored
            make_recipe(
                'legalaid.case', reference='ref5',
                provider=self.provider,
                outcome_code='IRCB'
            ),

            # obj6 accepted by provider => accepted
            make_recipe(
                'legalaid.case', reference='ref6',
                provider=self.provider,
                provider_viewed=timezone.now(),
                provider_accepted=timezone.now(),
                provider_closed=None
            ),

            # obj7 closed by provider => closed
            make_recipe(
                'legalaid.case', reference='ref7',
                provider=self.provider,
                provider_viewed=timezone.now(),
                provider_accepted=timezone.now(),
                provider_closed=timezone.now()
            ),
        ]

    def test_all_cases(self):
        response = self.client.get(
            self.list_url, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(4, len(response.data['results']))
        self.assertItemsEqual(
            [c['reference'] for c in response.data['results']],
            ['ref3', 'ref4', 'ref6', 'ref7']
        )

    def test_new_cases(self):
        response = self.client.get(
            u'%s?only=new' % self.list_url, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data['results']))
        self.assertItemsEqual(
            [c['reference'] for c in response.data['results']],
            ['ref3']
        )

    def test_opened_cases(self):
        response = self.client.get(
            u'%s?only=opened' % self.list_url, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data['results']))
        self.assertItemsEqual(
            [c['reference'] for c in response.data['results']],
            ['ref4']
        )

    def test_accepted_cases(self):
        response = self.client.get(
            u'%s?only=accepted' % self.list_url, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data['results']))
        self.assertItemsEqual(
            [c['reference'] for c in response.data['results']],
            ['ref6']
        )

    def test_closed_cases(self):
        response = self.client.get(
            u'%s?only=closed' % self.list_url, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data['results']))
        self.assertItemsEqual(
            [c['reference'] for c in response.data['results']],
            ['ref7']
        )


class UpdateCaseTestCase(BaseUpdateCaseTestCase, BaseCaseTestCase):
    def test_patch_provider_notes_allowed(self):
        """
        Test that provider can post provider notes
        """
        self.assertEqual(CaseNotesHistory.objects.all().count(), 0)

        response = self.client.patch(
            self.detail_url, data={'provider_notes': 'abc123'},
            format='json', HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['provider_notes'], 'abc123')

        self.assertEqual(CaseNotesHistory.objects.all().count(), 1)
        case_history = CaseNotesHistory.objects.last()
        self.assertEqual(case_history.provider_notes, 'abc123')
        self.assertEqual(case_history.created_by, self.user)

    def test_patch_operator_notes_not_allowed(self):
        """
        Test that provider cannot post operator notes
        """
        self.assertEqual(CaseNotesHistory.objects.all().count(), 0)
        response = self.client.patch(
            self.detail_url, data={'notes': 'abc123'},
            format='json', HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data['notes'], 'abc123')
        self.assertEqual(CaseNotesHistory.objects.all().count(), 0)


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

    def _test_provider_closed(self, code, expected_None):
        data = self.get_default_post_data()
        data['event_code'] = code

        self.assertEqual(self.resource.provider_closed, None)
        self._test_successful(data=data)

        self.resource = self.resource.__class__.objects.get(
            pk=self.resource.pk
        )
        if expected_None:
            self.assertNotEqual(self.resource.provider_closed, None)
        else:
            self.assertEqual(self.resource.provider_closed, None)

    def test_MIS_OOS_successful(self):
        self._test_provider_closed('MIS-OOS', True)

    def test_MIS_MEANS_successful(self):
        self._test_provider_closed('MIS-MEANS', True)

    def test_MIS_successful(self):
        self._test_provider_closed('MIS', False)

    def test_COI_successful(self):
        self._test_provider_closed('COI', False)


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

    def test_successful(self):
        self.assertEqual(self.resource.provider_closed, None)

        super(CloseCaseTestCase, self).test_successful()

        self.resource = self.resource.__class__.objects.get(
            pk=self.resource.pk
        )
        self.assertNotEqual(self.resource.provider_closed, None)


class ReopenCaseTestCase(ImplicitEventCodeViewTestCaseMixin, BaseCaseTestCase):
    NO_BODY_RESPONSE = False

    def setUp(self):
        super(ReopenCaseTestCase, self).setUp()
        self.resource.provider_closed = timezone.now()
        self.resource.save()

    def get_url(self, reference=None):
        reference = reference or self.resource.reference
        return reverse(
            'cla_provider:case-reopen', args=(),
            kwargs={'reference': reference}
        )

    def test_fails_if_case_not_closed(self):
        # setting provider closed to None
        self.resource.provider_closed = None
        self.resource.save()

        # before, no logs
        self.assertEqual(Log.objects.count(), 0)

        response = self.client.post(
            self.url, data={
                'notes': 'lorem ipsum'
            }, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.data, {
            '__all__': [u"You can't reopen this case as it's still open"]
        })

        # still no log
        self.assertEqual(Log.objects.count(), 0)

    def test_notes_mandatory(self):
        # before, no logs
        self.assertEqual(Log.objects.count(), 0)

        response = self.client.post(
            self.url, data={}, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.data, {
            'notes': [u'This field is required.']
        })

        # still no log
        self.assertEqual(Log.objects.count(), 0)


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
            'notes': 'Notes',
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
        self.assertEqual(Log.objects.count(), 3)

        new_case = self.resource.split_cases.first()
        ref_log = Log.objects.filter(case=new_case)[0]
        self.assertEqual(ref_log.notes, 'Notes')
