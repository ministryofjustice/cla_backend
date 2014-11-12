import mock
from django.test import TestCase

from cla_common.constants import REQUIRES_ACTION_BY

from core.tests.mommy_utils import make_recipe, make_user

from cla_eventlog.tests.test_forms import BaseCaseLogFormTestCaseMixin, \
    EventSpecificLogFormTestCaseMixin

from diagnosis.models import DiagnosisTraversal

from legalaid.tests.test_models import get_full_case
from legalaid.models import Case, AdaptationDetails, \
    CaseKnowledgebaseAssignment, Deductions, EligibilityCheck, Income, \
    Person, PersonalDetails, Property, Savings, ThirdPartyDetails
from cla_provider.forms import CloseCaseForm, AcceptCaseForm, \
    RejectCaseForm, SplitCaseForm


class AcceptCaseFormTestCase(BaseCaseLogFormTestCaseMixin, TestCase):
    FORM = AcceptCaseForm


class RejectCaseFormTestCase(EventSpecificLogFormTestCaseMixin, TestCase):
    FORM = RejectCaseForm

    def _test_provider_closed(self, code, expected_None):
        case = make_recipe('legalaid.case')
        data = self.get_default_data()
        data['event_code'] = code

        self.assertEqual(case.provider_closed, None)
        self._test_save_successfull(case=case, data=data)

        if expected_None:
            self.assertNotEqual(case.provider_closed, None)
        else:
            self.assertEqual(case.provider_closed, None)

    def test_save_MIS_OOS_sets_provider_closed(self):
        self._test_provider_closed('MIS-OOS', expected_None=True)

    def test_save_MIS_MEANS_sets_provider_closed(self):
        self._test_provider_closed('MIS-MEANS', expected_None=True)

    def test_save_MIS_doesnt_set_provider_closed(self):
        self._test_provider_closed('MIS', expected_None=False)

    def test_save_COI_doesnt_set_provider_closed(self):
        self._test_provider_closed('COI', expected_None=False)


class CloseCaseFormTestCase(BaseCaseLogFormTestCaseMixin, TestCase):
    FORM = CloseCaseForm

    def test_save_successfull(self):
        case = make_recipe('legalaid.case')

        self.assertEqual(case.provider_closed, None)
        self._test_save_successfull(case=case)

        self.assertNotEqual(case.provider_closed, None)


class SplitCaseFormTestCase(TestCase):

    def build_category_data(self):
        class CatData:
            def __init__(self):
                self.category = make_recipe('legalaid.category')
                self.matter_type1 = make_recipe(
                    'legalaid.matter_type1', category=self.category
                )
                self.matter_type2 = make_recipe(
                    'legalaid.matter_type2', category=self.category
                )
        return CatData()

    def setUp(self):
        super(SplitCaseFormTestCase, self).setUp()

        self.cat1_data = self.build_category_data()
        self.cat2_data = self.build_category_data()
        self.cat3_data = self.build_category_data()

        self.provider = make_recipe(
            'cla_provider.provider', law_category=[
                self.cat1_data.category, self.cat2_data.category,
            ]
        )
        self.request = mock.MagicMock(
            user=mock.MagicMock(
                staff=mock.MagicMock(
                    provider=self.provider
                )
            )
        )
        self.eligibility_check = make_recipe(
            'legalaid.eligibility_check',
            category=self.cat1_data.category
        )
        self.case = make_recipe(
            'legalaid.case', provider=self.provider,
            requires_action_by=REQUIRES_ACTION_BY.PROVIDER,
            eligibility_check=self.eligibility_check,
            matter_type1=self.cat1_data.matter_type1,
            matter_type2=self.cat1_data.matter_type2
        )

    def get_default_data(self, **kwargs):
        defaults = {
            'category': self.cat2_data.category.code,
            'matter_type1': self.cat2_data.matter_type1.code,
            'matter_type2': self.cat2_data.matter_type2.code,
            'internal': True
        }
        defaults.update(kwargs)
        return defaults

    # VALIDATION

    def test_invalid_if_case_doesnt_have_category(self):
        def test_invalid(case):
            form = SplitCaseForm(
                case=self.case, request=self.request,
                data=self.get_default_data()
            )
            self.assertFalse(form.is_valid())
            self.assertDictEqual(form.errors, {
                '__all__': ['The selected Case doesn\'t have any category associated.']
            })

        # CASE 1: case.eligibility_check.category == None
        self.case.eligibility_check.category = None
        self.case.eligibility_check.save()
        test_invalid(self.case)

        # CASE 2: case.eligibility_check == None
        self.case.eligibility_check = None
        self.case.save()
        test_invalid(self.case)

    def test_invalid_case_of_different_provider(self):
        def test_invalid(case):
            form = SplitCaseForm(
                case=case, request=self.request,
                data=self.get_default_data()
            )
            self.assertFalse(form.is_valid())
            self.assertDictEqual(form.errors, {
                '__all__': ['Only Providers assigned to the Case can split it.']
            })

        # CASE 1: case assigned to different provider
        different_provider = make_recipe('cla_provider.provider')

        self.case.provider = different_provider
        self.case.save()

        test_invalid(self.case)

        # CASE 2: case in the operator queue
        self.case.provider = None
        self.case.requires_action_by = REQUIRES_ACTION_BY.OPERATOR
        self.case.save()

        test_invalid(self.case)

    def test_invalid_basic(self):
        # 1. EMPTY DATA
        form = SplitCaseForm(
            case=self.case, request=self.request, data={}
        )
        self.assertFalse(form.is_valid())
        self.assertDictEqual(form.errors, {
            'category': ['This field is required.'],
            'matter_type1': ['This field is required.'],
            'matter_type2': ['This field is required.'],
        })

        # 2. INVALID DATA
        form = SplitCaseForm(
            case=self.case, request=self.request,
            data=self.get_default_data(
                category='invalid',
                matter_type1='invalid',
                matter_type2='invalid'
            )
        )
        self.assertFalse(form.is_valid())
        self.assertDictEqual(form.errors, {
            'category': ['Select a valid choice. That choice is not one of the available choices.'],
            'matter_type1': ['Select a valid choice. That choice is not one of the available choices.'],
            'matter_type2': ['Select a valid choice. That choice is not one of the available choices.'],
        })

    def test_invalid_matter_types_in_error(self):
        """
            - matter types not belonging to selected category
            - matter types levels not matching
        """

        # 1. MATTER TYPES NOT BELONGING TO SELECTED CATEGORY
        form = SplitCaseForm(
            case=self.case, request=self.request,
            data=self.get_default_data(
                category=self.cat2_data.category.code,
                matter_type1=self.cat3_data.matter_type1.code,
                matter_type2=self.cat3_data.matter_type2.code
            )
        )
        self.assertFalse(form.is_valid())
        self.assertDictEqual(form.errors, {
            'matter_type1': ['Select a valid choice. That choice is not one of the available choices.'],
            'matter_type2': ['Select a valid choice. That choice is not one of the available choices.'],
        })

        # 2. MATTER TYPES LEVELS NOT MATCHING
        form = SplitCaseForm(
            case=self.case, request=self.request,
            data=self.get_default_data(
                category=self.cat2_data.category.code,
                matter_type1=self.cat2_data.matter_type2.code,
                matter_type2=self.cat2_data.matter_type1.code
            )
        )
        self.assertFalse(form.is_valid())
        self.assertDictEqual(form.errors, {
            'matter_type1': ['Select a valid choice. That choice is not one of the available choices.'],
            'matter_type2': ['Select a valid choice. That choice is not one of the available choices.'],
        })

    def test_invalid_same_category(self):
        form = SplitCaseForm(
            case=self.case, request=self.request,
            data=self.get_default_data(
                category=self.cat1_data.category.code,
                matter_type1=self.cat1_data.matter_type1.code,
                matter_type2=self.cat1_data.matter_type2.code
            )
        )
        self.assertFalse(form.is_valid())
        self.assertDictEqual(form.errors, {
            'category': ['Please choose a different category or law.']
        })

    def test_invalid_internal_provider_cant_deal_with_category(self):
        form = SplitCaseForm(
            case=self.case, request=self.request,
            data=self.get_default_data(
                category=self.cat3_data.category.code,
                matter_type1=self.cat3_data.matter_type1.code,
                matter_type2=self.cat3_data.matter_type2.code,
                internal=True
            )
        )
        self.assertFalse(form.is_valid())
        self.assertDictEqual(form.errors, {
            'internal': ['Internal can only be choosen if you can deal with the selected Category of Law.']
        })

    def test_cannot_split_again(self):
        self.case.from_case = make_recipe('legalaid.case')
        self.case.save()

        form = SplitCaseForm(
            case=self.case, request=self.request,
            data=self.get_default_data(
                category=self.cat2_data.category.code,
                matter_type1=self.cat2_data.matter_type1.code,
                matter_type2=self.cat2_data.matter_type2.code,
                internal=False
            )
        )
        self.assertFalse(form.is_valid())
        self.assertDictEqual(
            form.errors,
            {'__all__': ['This Case has already been split or it has been generated by another Case']}
        )

    # SAVE

    @mock.patch('cla_provider.forms.event_registry')
    def test_rollback_on_unexpected_exception_during_save(self, mocked_event_registry):
        """
        In case of unexpected Exception, we don't want to have any rubbish
        objects in the db
        """
        mocked_event_registry.get_event.side_effect = Exception()

        case = get_full_case(
            self.cat2_data.matter_type1, self.cat2_data.matter_type2,
            provider=self.provider
        )

        expected_counts = {}
        for Model in [
            AdaptationDetails, Case, CaseKnowledgebaseAssignment, Deductions,
            EligibilityCheck, Income, Person, PersonalDetails, Property,
            Savings, ThirdPartyDetails, DiagnosisTraversal
        ]:
            expected_counts[Model] = Model.objects.count()

        form = SplitCaseForm(
            case=case, request=self.request,
            data=self.get_default_data(
                category=self.cat2_data.category.code,
                matter_type1=self.cat2_data.matter_type1.code,
                matter_type2=self.cat2_data.matter_type2.code,
                internal=False
            )
        )
        self.assertTrue(form.is_valid())
        self.assertRaises(Exception, form.save, make_user())

        self.assertTrue(expected_counts)
        for Model, expected_count in expected_counts.items():
            self.assertEqual(
                Model.objects.count(), expected_count,
                '%s count Expected to be %s but it\'s %s instead' % (
                    Model, expected_count, Model.objects.count()
                )
            )

    def _test_save_with_outcome(self, internal):
        if internal:
            outcome_code = 'REF-INT'
            system_outcome_code = 'REF-INT_CREATED'
        else:
            outcome_code = 'REF-EXT'
            system_outcome_code = 'REF-EXT_CREATED'

        case_log_set_size = self.case.log_set.count()

        self.assertEqual(Case.objects.count(), 1)
        form = SplitCaseForm(
            case=self.case, request=self.request,
            data=self.get_default_data(
                category=self.cat2_data.category.code,
                matter_type1=self.cat2_data.matter_type1.code,
                matter_type2=self.cat2_data.matter_type2.code,
                notes='Notes',
                internal=internal
            )
        )
        self.assertTrue(form.is_valid())

        user = make_user()
        new_case = form.save(user)
        self.assertEqual(Case.objects.count(), 2)

        # xxx_CREATED outcome codes for original case
        self.assertEqual(self.case.log_set.count(), case_log_set_size+1)
        original_case_log = self.case.log_set.last()
        self.assertEqual(original_case_log.code, system_outcome_code)
        self.assertEqual(
            original_case_log.notes,
            'Split case created and referred %s' % (
                'internally' if internal else 'externally'
            )
        )

        # 2 outcome codes for new case
        log_entries = new_case.log_set.order_by('created')
        self.assertEqual(len(log_entries), 2)

        # 1st CASE_CREATED
        log_created = log_entries[0]
        self.assertEqual(log_created.code, 'CASE_CREATED')
        self.assertEqual(log_created.notes, 'Case created by Specialist')
        self.assertEqual(log_created.created_by, user)

        # 2nd REF-INT or REF-EXT
        log_ref = log_entries[1]
        self.assertEqual(log_ref.code, outcome_code)
        self.assertEqual(log_ref.notes, 'Notes')
        self.assertEqual(log_ref.created_by, user)

    def test_save_internal(self):
        self._test_save_with_outcome(True)

    def test_save_external(self):
        self._test_save_with_outcome(False)
