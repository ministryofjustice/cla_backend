from django.conf import settings
from django.test import TestCase

from eligibility_calculator.models import CaseData, ModelMixin

from cla_common.constants import CASE_STATES
from cla_common.money_interval.models import MoneyInterval

from core.tests.mommy_utils import make_recipe, make_user

from legalaid.exceptions import InvalidMutationException
from ..models import Case

from cla_backend.apps.legalaid.models import Income



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
        check = make_recipe('legalaid.eligibility_check',
            category=make_recipe('legalaid.category', code='code'),
            you=make_recipe('legalaid.person',
                income= make_recipe('legalaid.income',
                    earnings= {"interval_period": "per_month",
                               "per_interval_value": 500,
                                },
                    other_income={"interval_period": "per_month",
                                  "per_interval_value": 600
                                  },
                    self_employed=True
                ),
                savings=make_recipe('legalaid.savings',
                    bank_balance=100,
                    investment_balance=200,
                    asset_balance=300,
                    credit_balance=400,
                ),
                deductions=make_recipe('legalaid.deductions',
                    income_tax=MoneyInterval('per_month', pennies=600),
                    national_insurance=MoneyInterval('per_month', pennies=100),
                    maintenance=MoneyInterval('per_month', pennies=710),
                    childcare=MoneyInterval('per_month', pennies=715),
                    mortgage=MoneyInterval('per_month', pennies=700),
                    rent=MoneyInterval('per_month', pennies=20),
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
                    'on_nass_benefits':False,
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
                        'other_income': 600,
                        'self_employed': True,
                    },
                    'deductions': {
                        'income_tax': 600,
                        'national_insurance': 100,
                        'maintenance': 710,
                        'childcare': 715,
                        'mortgage': 700,
                        'rent': 20,
                        'criminal_legalaid_contributions': 730,
                    }
                },
                property_data=[]
        ))

    def test_to_case_data_with_partner(self):
        """
        EligibilityCheck partner data is used during CaseData creation
        """
        check = make_recipe('legalaid.eligibility_check',
            category=make_recipe('legalaid.category', code='code'),
            you=make_recipe('legalaid.person',
                income=make_recipe('legalaid.income',
                    earnings=MoneyInterval('per_month', pennies=500),
                    other_income=MoneyInterval('per_month', pennies=600),
                    self_employed=True
                ),
                savings=make_recipe('legalaid.savings',
                    bank_balance=100,
                    investment_balance=200,
                    asset_balance=300,
                    credit_balance=400,
                ),
                deductions=make_recipe('legalaid.deductions',
                    income_tax=MoneyInterval('per_month', pennies=600),
                    national_insurance=MoneyInterval('per_month', pennies=100),
                    maintenance=MoneyInterval('per_month', pennies=710),
                    childcare=MoneyInterval('per_month', pennies=715),
                    mortgage=MoneyInterval('per_month', pennies=700),
                    rent=MoneyInterval('per_month', pennies=20),
                    criminal_legalaid_contributions=730
                )
            ),
            partner=make_recipe('legalaid.person',
                income= make_recipe('legalaid.income',
                    earnings=MoneyInterval('per_month', pennies=501),
                    other_income=MoneyInterval('per_month', pennies=601),
                    self_employed=False
                ),
                savings= make_recipe('legalaid.savings',
                    bank_balance=101,
                    investment_balance=201,
                    asset_balance=301,
                    credit_balance=401,
                ),
                deductions=make_recipe('legalaid.deductions',
                    income_tax=MoneyInterval('per_month', pennies=700),
                    national_insurance=MoneyInterval('per_month', pennies=1),
                    maintenance=MoneyInterval('per_month', pennies=711),
                    childcare=MoneyInterval('per_month', pennies=716),
                    mortgage=MoneyInterval('per_month', pennies=720),
                    rent=MoneyInterval('per_month', pennies=1),
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
                'on_nass_benefits':False,
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
                    'income_tax': 600,
                    'national_insurance': 100,
                    'maintenance': 710,
                    'childcare': 715,
                    'mortgage': 700,
                    'rent': 20,
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
                    'income_tax': 700,
                    'national_insurance': 1,
                    'maintenance': 711,
                    'childcare': 716,
                    'mortgage': 720,
                    'rent': 1,
                    'criminal_legalaid_contributions': 731,
                }
            },
            property_data=[],
        ))

    # def test_to_case_data_with_properties(self):
    #     """
    #     Tests with non-empty property set
    #     """
    #     check = make_recipe('legalaid.eligibility_check',
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
    #     make_recipe('legalaid.property',
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

    def test_create_has_laa_reference(self):
        case = make_recipe('legalaid.case')

        # there is an LAA Reference
        self.assertIsNotNone(case.laa_reference)

        # it is valid as per algorithm
        self.assertEqual(case.id + settings.LAA_REFERENCE_SEED, case.laa_reference)

        # it is 7 digits long
        self.assertEqual(len(unicode(case.laa_reference)), 7)


    def test_assign_to_provider_overriding_provider(self):
        providers = make_recipe('cla_provider.provider', _quantity=2)

        case = make_recipe('legalaid.case', provider=providers[0])

        self.assertTrue(case.provider)

        case.assign_to_provider(providers[1])

        self.assertEqual(case.provider, providers[1])

    def test_assign_to_provider_None(self):
        provider = make_recipe('cla_provider.provider')

        case = make_recipe('legalaid.case', provider=None)

        self.assertFalse(case.provider)

        case.assign_to_provider(provider)

        self.assertEqual(case.provider, provider)

    def test_lock_doesnt_override_existing_lock(self):
        import logging

        # disabling logging temporarily
        logging.disable(logging.CRITICAL)

        users = make_user(_quantity=2)
        case = make_recipe('legalaid.case',
            locked_by=users[0]
        )
        self.assertFalse(case.lock(users[1]))
        self.assertEqual(case.locked_by, users[0])

        # enabling logging back
        logging.disable(logging.NOTSET)

    def test_lock_without_saving(self):
        user = make_user()
        case = make_recipe('legalaid.case')
        self.assertTrue(case.lock(user, save=False))
        self.assertEqual(case.locked_by, user)

        db_case = Case.objects.get(pk=case.pk)
        self.assertEqual(db_case.locked_by, None)

    def test_lock_and_save(self):
        user = make_user()
        case = make_recipe('legalaid.case')
        self.assertTrue(case.lock(user))
        self.assertEqual(case.locked_by, user)

        db_case = Case.objects.get(pk=case.pk)
        self.assertEqual(db_case.locked_by, user)

    def test_is_open(self):
        # False
        case1 = make_recipe('legalaid.case', state=CASE_STATES.CLOSED)
        self.assertFalse(case1.is_open())

        # True
        case2 = make_recipe('legalaid.case', state=CASE_STATES.OPEN)
        self.assertTrue(case2.is_open())

    def test_is_closed(self):
        # False
        case1 = make_recipe('legalaid.case', state=CASE_STATES.CLOSED)
        self.assertTrue(case1.is_closed())

        # True
        case2 = make_recipe('legalaid.case', state=CASE_STATES.OPEN)
        self.assertFalse(case2.is_closed())

    def test_close_open_case(self):
        case = make_recipe('legalaid.case', state=CASE_STATES.OPEN)
        self.assertEqual(case.state, CASE_STATES.OPEN)

        self.assertTrue(case.close())

        case = Case.objects.get(pk=case.pk)
        self.assertEqual(case.state, CASE_STATES.CLOSED)

    def test_close_closed_case(self):
        """
            Should raise InvalidMutationException
        """
        # case closed already
        case = make_recipe('legalaid.case', state=CASE_STATES.CLOSED)
        self.assertEqual(case.state, CASE_STATES.CLOSED)

        with self.assertRaises(InvalidMutationException):
            case.close()

        case = Case.objects.get(pk=case.pk)
        self.assertEqual(case.state, CASE_STATES.CLOSED)

        # case closed rejected
        case = make_recipe('legalaid.case', state=CASE_STATES.REJECTED)
        self.assertEqual(case.state, CASE_STATES.REJECTED)

        with self.assertRaises(InvalidMutationException):
            case.close()

        case = Case.objects.get(pk=case.pk)
        self.assertEqual(case.state, CASE_STATES.REJECTED)

    # REJECT

    def test_reject_open_case(self):
        """
        Reject successfull
        """
        case = make_recipe('legalaid.case', state=CASE_STATES.OPEN)
        self.assertEqual(case.state, CASE_STATES.OPEN)

        case.reject()

        case = Case.objects.get(pk=case.pk)
        self.assertEqual(case.state, CASE_STATES.REJECTED)

    def test_reject_closed_case(self):
        """
            Should raise InvalidMutationException
        """
        case = make_recipe('legalaid.case', state=CASE_STATES.CLOSED)
        self.assertEqual(case.state, CASE_STATES.CLOSED)

        with self.assertRaises(InvalidMutationException):
            case.reject()

        case = Case.objects.get(pk=case.pk)
        self.assertEqual(case.state, CASE_STATES.CLOSED)

    # ACCEPT

    def test_accept_open_case(self):
        """
        Accept successfull
        """
        case = make_recipe('legalaid.case', state=CASE_STATES.OPEN)
        self.assertEqual(case.state, CASE_STATES.OPEN)

        case.accept()

        case = Case.objects.get(pk=case.pk)
        self.assertEqual(case.state, CASE_STATES.ACCEPTED)

    def test_accept_closed_case(self):
        """
            Should raise InvalidMutationException
        """

        case = make_recipe('legalaid.case', state=CASE_STATES.CLOSED)
        self.assertEqual(case.state, CASE_STATES.CLOSED)

        with self.assertRaises(InvalidMutationException):
            case.accept()

        case = Case.objects.get(pk=case.pk)
        self.assertEqual(case.state, CASE_STATES.CLOSED)


class MoneyIntervalFieldTestCase(TestCase):
    def test_create_save_moneyinterval(self):

        ei = MoneyInterval('per_week', pennies=5000)
        per_month = int((5000.0 * 52.0) / 12.0)

        i = Income(earnings=ei, other_income=ei, self_employed=True)
        self.assertEqual(i.earnings.interval_period, 'per_week')
        i.save()

        ix = Income.objects.get(id=i.id)
        eix = ix.earnings
        self.assertEqual(eix.interval_period, 'per_week')
        self.assertEqual(eix.per_interval_value, 5000)
        self.assertEqual(eix.as_monthly(), per_month)

    def test_annual_moneyinterval(self):

        ei = MoneyInterval(interval_period='per_year', pennies=1200000)
        self.assertEqual(ei.as_monthly(), 100000)

