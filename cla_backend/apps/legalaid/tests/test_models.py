from django.test import TestCase
from django.conf import settings

from model_mommy import mommy

from eligibility_calculator.models import CaseData, ModelMixin

from cla_common.constants import CASE_STATE_OPEN, CASE_STATE_CLOSED, \
    CASE_STATE_REJECTED, CASE_STATE_ACCEPTED

from ..models import Case


def make_recipe(model_name, **kwargs):
    return mommy.make_recipe('legalaid.tests.%s' % model_name, **kwargs)


def cla_provider_make_recipe(model_name, **kwargs):
    return mommy.make_recipe('cla_provider.tests.%s' % model_name, **kwargs)


def walk(coll):
    """Return a generator for all atomic values in coll and its subcollections.
    An atomic value is one that's not iterable as determined by iter."""
    try:
        k = iter(coll)
        for x in k:
            for y in walk(x):
                yield y
    except TypeError:
        yield coll


class EligibilityCheckTestCase(TestCase):

    # def test_to_case_data_fail_without_your_finances(self):
    #     """
    #     Should fail as your_finances object is always needed
    #     """
    #     check = EligibilityCheck()
    #
    #     self.assertRaises(ValueError, check.to_case_data)

    def assertModelMixinEqual(self, obj1, obj2):
        for prop in obj1.__class__.PROPERTY_META.keys():
            if hasattr(obj1, prop) or hasattr(obj2, prop):
                val1 = getattr(obj1, prop)
                val2 = getattr(obj2, prop)

                assertFunc = self.assertEqual
                if isinstance(val1, list) or isinstance(val2, list):
                    assertFunc = self.assertItemsEqual
                if isinstance(val1, ModelMixin) or isinstance(val2, ModelMixin):
                    self.assertModelMixinEqual(val1, val2)
                    continue

                assertFunc(val1, val2, u"%s: %s != %s" % (prop, val1, val2))

    def test_to_case_data_without_partner(self):
        """
        EligibilityCheck partner data won't be used during CaseData creation
        """
        check = make_recipe('eligibility_check',
            category=make_recipe('category', code='code'),
            you=make_recipe('person',
                income= make_recipe('income',
                    earnings=500,
                    other_income=600,
                    self_employed=True
                ),
                savings= make_recipe('savings',
                    bank_balance=100,
                    investment_balance=200,
                    asset_balance=300,
                    credit_balance=400,
                ),
                deductions=make_recipe('deductions',
                    income_tax_and_ni=700,
                    maintenance=710,
                    childcare=715,
                    mortgage_or_rent=720,
                    criminal_legalaid_contributions=730
                )
            ),
            dependants_young=3, dependants_old=2,
            is_you_or_your_partner_over_60=True,
            on_passported_benefits=True,
            has_partner=False,
        )

        case_data = check.to_case_data()
        self.assertModelMixinEqual(
            case_data,
            CaseData(
                category='code',
                facts={
                    'dependant_children':5,
                    'is_you_or_your_partner_over_60':True,
                    'on_passported_benefits':True,
                    'has_partner': False,
                    'is_partner_opponent': False,
                },
                you={
                    'savings':{
                        'savings':100,
                        'investments': 200,
                        'money_owed':400,
                        'valuable_items': 300,
                    },
                    'income': {
                        'earnings': 500,
                        'other_income':600,
                        'self_employed': True,
                    },
                    'deductions': {
                        'income_tax_and_ni': 700,
                        'maintenance': 710,
                        'childcare': 715,
                        'mortgage_or_rent': 720,
                        'criminal_legalaid_contributions': 730,
                    }
                },
                property_data=[]
        ))

    def test_to_case_data_with_partner(self):
        """
        EligibilityCheck partner data is used during CaseData creation
        """
        check = make_recipe('eligibility_check',
            category=make_recipe('category', code='code'),
            you=make_recipe('person',
                income=make_recipe('income',
                    earnings=500,
                    other_income=600,
                    self_employed=True
                ),
                savings= make_recipe('savings',
                    bank_balance=100,
                    investment_balance=200,
                    asset_balance=300,
                    credit_balance=400,
                ),
                deductions=make_recipe('deductions',
                    income_tax_and_ni=700,
                    maintenance=710,
                    childcare=715,
                    mortgage_or_rent=720,
                    criminal_legalaid_contributions=730
                )
            ),
            partner=make_recipe('person',
                income= make_recipe('income',
                    earnings=501,
                    other_income=601,
                    self_employed=False
                ),
                savings= make_recipe('savings',
                    bank_balance=101,
                    investment_balance=201,
                    asset_balance=301,
                    credit_balance=401,
                ),
                deductions=make_recipe('deductions',
                    income_tax_and_ni=701,
                    maintenance=711,
                    childcare=716,
                    mortgage_or_rent=721,
                    criminal_legalaid_contributions=731
                )
            ),
            dependants_young=3, dependants_old=2,
            is_you_or_your_partner_over_60=True,
            on_passported_benefits=True,
            has_partner=True,
        )

        case_data = check.to_case_data()
        self.assertModelMixinEqual(case_data, CaseData(
            category='code',
            facts={
                'dependant_children':5,
                'is_you_or_your_partner_over_60':True,
                'on_passported_benefits':True,
                'has_partner': True,
                'is_partner_opponent': False,
            },
            you={
                'savings':{
                    'savings':100,
                    'investments': 200,
                    'money_owed':400,
                    'valuable_items': 300,
                },
                'income': {
                    'earnings': 500,
                    'other_income':600,
                    'self_employed': True,
                },
                'deductions': {
                    'income_tax_and_ni': 700,
                    'maintenance': 710,
                    'childcare': 715,
                    'mortgage_or_rent': 720,
                    'criminal_legalaid_contributions': 730,
                }
            },
            partner={
                'savings':{
                    'savings':101,
                    'investments': 201,
                    'money_owed':401,
                    'valuable_items': 301,
                },
                'income': {
                    'earnings': 501,
                    'other_income':601,
                    'self_employed': False,
                },
                'deductions': {
                    'income_tax_and_ni': 701,
                    'maintenance': 711,
                    'childcare': 716,
                    'mortgage_or_rent': 721,
                    'criminal_legalaid_contributions': 731,
                }
            },
            property_data=[],
        ))

    # def test_to_case_data_with_properties(self):
    #     """
    #     Tests with non-empty property set
    #     """
    #     check = make_recipe('eligibility_check',
    #         category=make_recipe('category', code='code'),
    #         your_finances=make_recipe('finance',
    #             bank_balance=100, investment_balance=200,
    #             asset_balance=300, credit_balance=400,
    #             earnings=500, other_income=600,
    #             self_employed=True, income_tax_and_ni=700,
    #             maintenance=710, mortgage_or_rent=720,
    #             criminal_legalaid_contributions=730
    #         ),
    #         dependants_young=3, dependants_old=2,
    #         is_you_or_your_partner_over_60=True,
    #         on_passported_benefits=True,
    #         has_partner=False,
    #     )
    #     make_recipe('property',
    #         eligibility_check=check,
    #         value=recipe.seq(30), mortgage_left=recipe.seq(40),
    #         share=recipe.seq(50), _quantity=3
    #     )
    #
    #     case_data = check.to_case_data()
    #     self.assertCaseDataEqual(case_data, CaseData(
    #         category='code', dependant_children=5, savings=100, investments=200,
    #         money_owed=400, valuable_items=300, earnings=500, other_income=600,
    #         self_employed=True, property_data=[(31, 41, 51), (32, 42, 52), (33, 43, 53)],
    #         is_you_or_your_partner_over_60=True,
    #         has_partner=False, is_partner_opponent=False, income_tax_and_ni=700,
    #         maintenance=710, mortgage_or_rent=720,
    #         criminal_legalaid_contributions=730,
    #         on_passported_benefits=True
    #     ))


class CaseTestCase(TestCase):
    def test_assign_to_provider_overriding_provider(self):
        providers = cla_provider_make_recipe('provider', _quantity=2)

        case = make_recipe('case', provider=providers[0])

        self.assertTrue(case.provider)

        case.assign_to_provider(providers[1])

        self.assertEqual(case.provider, providers[1])

    def test_assign_to_provider_None(self):
        provider = cla_provider_make_recipe('provider')

        case = make_recipe('case', provider=None)

        self.assertFalse(case.provider)

        case.assign_to_provider(provider)

        self.assertEqual(case.provider, provider)

    def test_lock_doesnt_override_existing_lock(self):
        import logging

        # disabling logging temporarily
        logging.disable(logging.CRITICAL)

        users = mommy.make(settings.AUTH_USER_MODEL, _quantity=2)
        case = make_recipe('case',
            locked_by=users[0]
        )
        self.assertFalse(case.lock(users[1]))
        self.assertEqual(case.locked_by, users[0])

        # enabling logging back
        logging.disable(logging.NOTSET)

    def test_lock_without_saving(self):
        user = mommy.make(settings.AUTH_USER_MODEL)
        case = make_recipe('case')
        self.assertTrue(case.lock(user, save=False))
        self.assertEqual(case.locked_by, user)

        db_case = Case.objects.get(pk=case.pk)
        self.assertEqual(db_case.locked_by, None)

    def test_lock_and_save(self):
        user = mommy.make(settings.AUTH_USER_MODEL)
        case = make_recipe('case')
        self.assertTrue(case.lock(user))
        self.assertEqual(case.locked_by, user)

        db_case = Case.objects.get(pk=case.pk)
        self.assertEqual(db_case.locked_by, user)

    def test_is_open(self):
        # False
        case1 = make_recipe('case', state=CASE_STATE_CLOSED)
        self.assertFalse(case1.is_open())

        # True
        case2 = make_recipe('case', state=CASE_STATE_OPEN)
        self.assertTrue(case2.is_open())

    def test_is_closed(self):
        # False
        case1 = make_recipe('case', state=CASE_STATE_CLOSED)
        self.assertTrue(case1.is_closed())

        # True
        case2 = make_recipe('case', state=CASE_STATE_OPEN)
        self.assertFalse(case2.is_closed())

    def test_close_open_case(self):
        case = make_recipe('case', state=CASE_STATE_OPEN)
        self.assertEqual(case.state, CASE_STATE_OPEN)

        self.assertTrue(case.close())

        case = Case.objects.get(pk=case.pk)
        self.assertEqual(case.state, CASE_STATE_CLOSED)

    def test_close_closed_case(self):
        """
            Shouldn't do anything apart from logging the event
        """
        import logging

        # disabling logging temporarily
        logging.disable(logging.CRITICAL)

        case = make_recipe('case', state=CASE_STATE_CLOSED)
        self.assertEqual(case.state, CASE_STATE_CLOSED)

        self.assertFalse(case.close())

        case = Case.objects.get(pk=case.pk)
        self.assertEqual(case.state, CASE_STATE_CLOSED)

        # enabling logging back
        logging.disable(logging.NOTSET)

    def test_reject_open_case(self):
        """
        Reject successfull
        """
        case = make_recipe('case', state=CASE_STATE_OPEN)
        self.assertEqual(case.state, CASE_STATE_OPEN)

        self.assertTrue(case.reject())

        case = Case.objects.get(pk=case.pk)
        self.assertEqual(case.state, CASE_STATE_REJECTED)

    def test_reject_closed_case(self):
        """
            Shouldn't do anything apart from logging the event
        """
        import logging

        # disabling logging temporarily
        logging.disable(logging.CRITICAL)

        case = make_recipe('case', state=CASE_STATE_CLOSED)
        self.assertEqual(case.state, CASE_STATE_CLOSED)

        self.assertFalse(case.reject())

        case = Case.objects.get(pk=case.pk)
        self.assertEqual(case.state, CASE_STATE_CLOSED)

        # enabling logging back
        logging.disable(logging.NOTSET)

    def test_accept_open_case(self):
        """
        Accept successfull
        """
        case = make_recipe('case', state=CASE_STATE_OPEN)
        self.assertEqual(case.state, CASE_STATE_OPEN)

        self.assertTrue(case.accept())

        case = Case.objects.get(pk=case.pk)
        self.assertEqual(case.state, CASE_STATE_ACCEPTED)

    def test_accept_closed_case(self):
        """
            Shouldn't do anything apart from logging the event
        """
        import logging

        # disabling logging temporarily
        logging.disable(logging.CRITICAL)

        case = make_recipe('case', state=CASE_STATE_CLOSED)
        self.assertEqual(case.state, CASE_STATE_CLOSED)

        self.assertFalse(case.accept())

        case = Case.objects.get(pk=case.pk)
        self.assertEqual(case.state, CASE_STATE_CLOSED)

        # enabling logging back
        logging.disable(logging.NOTSET)
