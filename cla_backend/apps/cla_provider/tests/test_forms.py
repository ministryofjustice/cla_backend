import mock
from django.test import TestCase

from cla_common.constants import REQUIRES_ACTION_BY

from core.tests.mommy_utils import make_recipe, make_user

from cla_eventlog.tests.test_forms import BaseCaseLogFormTestCaseMixin, \
    EventSpecificLogFormTestCaseMixin

from legalaid.models import Case
from cla_provider.forms import CloseCaseForm, AcceptCaseForm, \
    RejectCaseForm, SplitCaseForm


class AcceptCaseFormTestCase(BaseCaseLogFormTestCaseMixin, TestCase):
    FORM = AcceptCaseForm


class RejectCaseFormTestCase(EventSpecificLogFormTestCaseMixin, TestCase):
    FORM = RejectCaseForm


class CloseCaseFormTestCase(BaseCaseLogFormTestCaseMixin, TestCase):
    FORM = CloseCaseForm


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
            'category': ['Select a valid choice. That choice is not one of the available choices.']
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

    # SAVE

    def _test_save_with_outcome(self, internal, outcome_code):
        self.assertEqual(Case.objects.count(), 1)
        form = SplitCaseForm(
            case=self.case, request=self.request,
            data=self.get_default_data(
                category=self.cat2_data.category.code,
                matter_type1=self.cat2_data.matter_type1.code,
                matter_type2=self.cat2_data.matter_type2.code,
                internal=internal
            )
        )
        self.assertTrue(form.is_valid())

        user = make_user()
        new_case = form.save(user)
        self.assertEqual(Case.objects.count(), 2)

        log_entry1 = self.case.log_set.last()
        self.assertEqual(log_entry1.code, outcome_code)
        self.assertEqual(log_entry1.created_by, user)

        log_entry2 = new_case.log_set.last()
        self.assertEqual(log_entry2.code, 'CASE_CREATED')
        self.assertEqual(log_entry2.notes, 'Case created by Specialist')
        self.assertEqual(log_entry2.created_by, user)

    def test_save_internal(self):
        self._test_save_with_outcome(True, 'REF-INT')

    def test_save_external(self):
        self._test_save_with_outcome(False, 'REF-EXT')
