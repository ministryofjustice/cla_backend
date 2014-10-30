import mock
import datetime
import random

from django.conf import settings
from django.test import TestCase
from django.db import models
from django.utils import timezone

from eligibility_calculator.models import CaseData, ModelMixin
from eligibility_calculator.exceptions import PropertyExpectedException

from cla_common.constants import ELIGIBILITY_STATES, CONTACT_SAFETY, \
    THIRDPARTY_REASON, THIRDPARTY_RELATIONSHIP, ADAPTATION_LANGUAGES, \
    REQUIRES_ACTION_BY, DIAGNOSIS_SCOPE, EXEMPT_USER_REASON, ECF_STATEMENT, \
    CASE_SOURCE
from cla_common.money_interval.models import MoneyInterval

from core.tests.mommy_utils import make_recipe, make_user

from legalaid.models import Savings, Income, Deductions, PersonalDetails, \
    ThirdPartyDetails, AdaptationDetails, Person, Case, ValidateModelMixin, \
    EligibilityCheck, Property, CaseKnowledgebaseAssignment


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


def get_full_case(matter_type1, matter_type2, provider=None):
    provider = provider or make_recipe('cla_provider.provider')

    ec = make_recipe(
        'legalaid.eligibility_check_yes',
        disputed_savings=make_recipe('legalaid.savings'),
        on_passported_benefits=True,
        on_nass_benefits=True,
        is_you_or_your_partner_over_60=True,
        has_partner=True,
        calculations={'disposable_income': 1000}
    )
    make_recipe(
        'legalaid.property', eligibility_check=ec,
        value=random.randint(1, 100),
        mortgage_left=random.randint(1, 100),
        share=random.randint(1, 100),
        disputed=True, main=True,
        _quantity=2
    )
    outcome = make_recipe('cla_eventlog.log')
    case = make_recipe(
        'legalaid.case',
        eligibility_check=ec,
        diagnosis=make_recipe('diagnosis.diagnosis_yes'),
        personal_details=make_recipe('legalaid.personal_details'),
        created_by=make_user(),
        requires_action_by=REQUIRES_ACTION_BY.PROVIDER_REVIEW,
        requires_action_at=timezone.now(),
        callback_attempt=2,
        locked_by=make_user(),
        locked_at=timezone.now(),
        provider=provider,
        notes='Notes',
        provider_notes='Provider Notes',
        thirdparty_details=make_recipe('legalaid.thirdparty_details'),
        adaptation_details=make_recipe('legalaid.adaptation_details'),
        billable_time=2000,
        matter_type1=matter_type1,
        matter_type2=matter_type2,
        media_code=make_recipe('legalaid.media_code'),
        outcome_code='outcome code',
        outcome_code_id=outcome.pk,
        level=40,
        exempt_user=True,
        exempt_user_reason=EXEMPT_USER_REASON.ECHI,
        ecf_statement=ECF_STATEMENT.READ_OUT_MESSAGE,
        source=CASE_SOURCE.WEB
    )
    CaseKnowledgebaseAssignment.objects.create(
        case=case, assigned_by=make_user(),
        alternative_help_article=make_recipe('knowledgebase.article')
    )

    return case


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
                    earnings=MoneyInterval('per_month', pennies=100),
                    self_employment_drawings=MoneyInterval('per_month', pennies=200),
                    benefits=MoneyInterval('per_month', pennies=300),
                    tax_credits=MoneyInterval('per_month', pennies=400),
                    child_benefits=MoneyInterval('per_month', pennies=500),
                    maintenance_received=MoneyInterval('per_month', pennies=600),
                    pension=MoneyInterval('per_month', pennies=700),
                    other_income=MoneyInterval('per_month', pennies=800),
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
            on_nass_benefits=False,
            has_partner=False,
        )

        case_data = check.to_case_data()
        self.assertModelMixinEqual(
            case_data,
            CaseData(
                category='code',
                facts={
                    'dependants_young': 3,
                    'dependants_old': 2,
                    'is_you_or_your_partner_over_60':True,
                    'on_passported_benefits':True,
                    'on_nass_benefits': False,
                    'has_partner': False,
                    'is_partner_opponent': False,
                },
                you={
                    'savings':{
                        'bank_balance':100,
                        'investment_balance': 200,
                        'credit_balance':400,
                        'asset_balance': 300,
                    },
                    'income': {
                        'earnings': 100,
                        'self_employment_drawings': 200,
                        'benefits': 300,
                        'tax_credits': 400,
                        'child_benefits': 500,
                        'maintenance_received': 600,
                        'pension': 700,
                        'other_income': 800,
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

    def test_to_case_data_with_partner_and_None_partner_child_benefits(self):
        """
        EligibilityCheck partner data is used during CaseData creation

        If partner.income.child_benefits is None, the to_case_data use a
        default value (0). This is because that field is not exposed yet
        (partner's child benefits can't be provided with).
        """
        check = make_recipe('legalaid.eligibility_check',
            category=make_recipe('legalaid.category', code='code'),
            you=make_recipe('legalaid.person',
                income=make_recipe('legalaid.income',
                    earnings=MoneyInterval('per_month', pennies=100),
                    self_employment_drawings=MoneyInterval('per_month', pennies=200),
                    benefits=MoneyInterval('per_month', pennies=300),
                    tax_credits=MoneyInterval('per_month', pennies=400),
                    child_benefits=MoneyInterval('per_month', pennies=500),
                    maintenance_received=MoneyInterval('per_month', pennies=600),
                    pension=MoneyInterval('per_month', pennies=700),
                    other_income=MoneyInterval('per_month', pennies=800),
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
                    earnings=MoneyInterval('per_month', pennies=101),
                    self_employment_drawings=MoneyInterval('per_month', pennies=201),
                    benefits=MoneyInterval('per_month', pennies=301),
                    tax_credits=MoneyInterval('per_month', pennies=401),
                    # child_beneficts will be None. Testing that the to_case_data sets a default 0 for
                    # this value.
                    child_benefits=None,
                    maintenance_received=MoneyInterval('per_month', pennies=601),
                    pension=MoneyInterval('per_month', pennies=701),
                    other_income=MoneyInterval('per_month', pennies=801),
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
            on_nass_benefits=False,
            has_partner=True,
        )

        case_data = check.to_case_data()
        self.assertModelMixinEqual(case_data, CaseData(
            category='code',
            facts={
                'dependants_young': 3,
                'dependants_old': 2,
                'is_you_or_your_partner_over_60':True,
                'on_passported_benefits': True,
                'on_nass_benefits': False,
                'has_partner': True,
                'is_partner_opponent': False,
            },
            you={
                'savings':{
                    'bank_balance':100,
                    'investment_balance': 200,
                    'credit_balance':400,
                    'asset_balance': 300,
                },
                'income': {
                    'earnings': 100,
                    'self_employment_drawings': 200,
                    'benefits': 300,
                    'tax_credits': 400,
                    'child_benefits': 500,
                    'maintenance_received': 600,
                    'pension': 700,
                    'other_income': 800,
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
                    'bank_balance':101,
                    'investment_balance': 201,
                    'credit_balance':401,
                    'asset_balance': 301,
                },
                'income': {
                    'earnings': 101,
                    'self_employment_drawings': 201,
                    'benefits': 301,
                    'tax_credits': 401,
                    'child_benefits': 0,
                    'maintenance_received': 601,
                    'pension': 701,
                    'other_income': 801,
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

    def test_to_case_data_with_partner_and_NOT_None_partner_child_benefits(self):
        """
        EligibilityCheck partner data is used during CaseData creation

        If partner.income.child_benefits is NOT None, the to_case_data will use
        that value and will not override it with 0
        """
        check = make_recipe('legalaid.eligibility_check',
            category=make_recipe('legalaid.category', code='code'),
            you=make_recipe('legalaid.person',
                income=make_recipe('legalaid.income',
                    earnings=MoneyInterval('per_month', pennies=100),
                    self_employment_drawings=MoneyInterval('per_month', pennies=200),
                    benefits=MoneyInterval('per_month', pennies=300),
                    tax_credits=MoneyInterval('per_month', pennies=400),
                    child_benefits=MoneyInterval('per_month', pennies=500),
                    maintenance_received=MoneyInterval('per_month', pennies=600),
                    pension=MoneyInterval('per_month', pennies=700),
                    other_income=MoneyInterval('per_month', pennies=800),
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
                    earnings=MoneyInterval('per_month', pennies=101),
                    self_employment_drawings=MoneyInterval('per_month', pennies=201),
                    benefits=MoneyInterval('per_month', pennies=301),
                    tax_credits=MoneyInterval('per_month', pennies=401),
                    # child_beneficts is not None. Testing that the to_case_data doesn't
                    # override this value
                    child_benefits=MoneyInterval('per_month', pennies=501),
                    maintenance_received=MoneyInterval('per_month', pennies=601),
                    pension=MoneyInterval('per_month', pennies=701),
                    other_income=MoneyInterval('per_month', pennies=801),
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
            on_nass_benefits=False,
            has_partner=True,
        )

        case_data = check.to_case_data()
        self.assertModelMixinEqual(case_data, CaseData(
            category='code',
            facts={
                'dependants_young': 3,
                'dependants_old': 2,
                'is_you_or_your_partner_over_60':True,
                'on_passported_benefits': True,
                'on_nass_benefits': False,
                'has_partner': True,
                'is_partner_opponent': False,
            },
            you={
                'savings':{
                    'bank_balance':100,
                    'investment_balance': 200,
                    'credit_balance':400,
                    'asset_balance': 300,
                },
                'income': {
                    'earnings': 100,
                    'self_employment_drawings': 200,
                    'benefits': 300,
                    'tax_credits': 400,
                    'child_benefits': 500,
                    'maintenance_received': 600,
                    'pension': 700,
                    'other_income': 800,
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
                    'bank_balance':101,
                    'investment_balance': 201,
                    'credit_balance':401,
                    'asset_balance': 301,
                },
                'income': {
                    'earnings': 101,
                    'self_employment_drawings': 201,
                    'benefits': 301,
                    'tax_credits': 401,
                    'child_benefits': 501,
                    'maintenance_received': 601,
                    'pension': 701,
                    'other_income': 801,
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

    def test_validate(self):
        check = make_recipe(
            'legalaid.eligibility_check',
            category=make_recipe('legalaid.category', code='code'),
            you=make_recipe('legalaid.person',
                income= make_recipe('legalaid.income',
                    earnings=MoneyInterval('per_month', pennies=500),
                    self_employment_drawings=MoneyInterval('per_month', pennies=200),
                    benefits=MoneyInterval('per_month', pennies=300),
                    tax_credits=MoneyInterval('per_month', pennies=400),
                    child_benefits=MoneyInterval('per_month', pennies=500),
                    maintenance_received=MoneyInterval('per_month', pennies=600),
                    pension=MoneyInterval('per_month', pennies=700),
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
            dependants_young=3, dependants_old=2,
            is_you_or_your_partner_over_60=True,
            on_passported_benefits=True,
            has_partner=True,
            )
        expected = {
            'warnings': {
                'partner': {
                    'deductions': ['Field "deductions" is required'],
                    'income': ['Field "income" is required'],
                    'savings': ['Field "savings" is required']
                }
            }
        }

        self.assertEqual(expected, check.validate())
        check.you = None
        expected2 = {
            'warnings': {
                'partner': {
                    'deductions': ['Field "deductions" is required'],
                    'income': ['Field "income" is required'],
                    'savings': ['Field "savings" is required']
                },
                'you': {
                    'deductions': ['Field "deductions" is required'],
                    'income': ['Field "income" is required'],
                    'savings': ['Field "savings" is required']
                }
            }
        }
        self.assertDictEqual(expected2, check.validate())

    @mock.patch('legalaid.models.EligibilityChecker')
    def test_update_state(self, MockedEligibilityChecker):
        """
            calling .is_eligible() sequencially will:

            1. through PropertyExpectedException
            2. return True
            3. return False
            4. through PropertyExpectedException again
        """
        mocked_checker = MockedEligibilityChecker()
        mocked_checker.calcs = {}
        mocked_checker.is_eligible.side_effect = [
            PropertyExpectedException(), True, False, PropertyExpectedException()
        ]

        # 1. PropertyExpectedException => UNKNOWN
        check = make_recipe('legalaid.eligibility_check', state=ELIGIBILITY_STATES.UNKNOWN)
        check.update_state()
        self.assertEqual(check.state, ELIGIBILITY_STATES.UNKNOWN)

        # 2. True => YES
        check.update_state()
        self.assertEqual(check.state, ELIGIBILITY_STATES.YES)

        # 3. False => NO
        check.update_state()
        self.assertEqual(check.state, ELIGIBILITY_STATES.NO)

        # 4. PropertyExpectedException => UNKNOWN
        check.update_state()
        self.assertEqual(check.state, ELIGIBILITY_STATES.UNKNOWN)


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

    def test_assign_to_provider_resets_callback_info(self):
        provider = make_recipe('cla_provider.provider')

        case = make_recipe(
            'legalaid.case',
            requires_action_at=timezone.now(),
            callback_attempt=2
        )

        self.assertNotEqual(case.requires_action_at, None)
        self.assertEqual(case.callback_attempt, 2)

        case.assign_to_provider(provider)

        self.assertEqual(case.provider, provider)
        self.assertEqual(case.requires_action_at, None)
        self.assertEqual(case.callback_attempt, 0)

    def test_assign_alternative_help(self):
        articles = make_recipe('knowledgebase.article', _quantity=10)
        user = make_user()
        case = make_recipe('legalaid.case', provider=None)

        # assign some articles
        self.assertListEqual(list(case.alternative_help_articles.all()), [])
        case.assign_alternative_help(user, articles[:5])
        self.assertListEqual(list(case.alternative_help_articles.all()), articles[:5])

        # assign some more articles; originals should be gone
        case.assign_alternative_help(user, articles[5:])

        self.assertListEqual(list(case.alternative_help_articles.all()), articles[5:])

    def test_assign_alternative_help_resets_callback_info(self):
        articles = make_recipe('knowledgebase.article', _quantity=10)
        user = make_user()
        case = make_recipe(
            'legalaid.case', provider=None,
            requires_action_at=timezone.now(),
            callback_attempt=2
        )

        self.assertNotEqual(case.requires_action_at, None)
        self.assertEqual(case.callback_attempt, 2)

        # assign some articles
        self.assertListEqual(list(case.alternative_help_articles.all()), [])
        case.assign_alternative_help(user, articles[:5])
        self.assertListEqual(list(case.alternative_help_articles.all()), articles[:5])

        self.assertEqual(case.requires_action_at, None)
        self.assertEqual(case.callback_attempt, 0)

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

    # CASE COUNT

    def test_case_count_doesnt_updated_if_null_pd(self):
        """
        if case.personal_details == None:
            case.personal_details.case_count shouldn't get updated
        """
        case = make_recipe('legalaid.case')
        self.assertTrue(case.personal_details, None)

    def test_case_count_gets_updated_if_pd_not_null(self):
        pd = make_recipe('legalaid.personal_details')

        self.assertEqual(pd.case_count, 0)
        # saving first case
        make_recipe('legalaid.case', personal_details=pd)
        self.assertEqual(pd.case_count, 1)

        # saving second case
        make_recipe('legalaid.case', personal_details=pd)
        self.assertEqual(pd.case_count, 2)

        # saving different case
        pd2 = make_recipe('legalaid.personal_details')
        make_recipe('legalaid.case', personal_details=pd2)
        self.assertEqual(pd.case_count, 2)
        self.assertEqual(pd2.case_count, 1)


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


class ValidationModelMixinTestCase(TestCase):

    class Model1(models.Model):
        pass

    class Model2(ValidateModelMixin, models.Model):
        pass

    class Model3(ValidateModelMixin, models.Model):

        a = models.CharField(null=True, blank=True)
        b = models.CharField(null=True, blank=True)
        c = models.CharField(null=True, blank=True)

        def get_dependencies(self):
            return {'a', 'b', 'c'}

    class Model4(ValidateModelMixin, models.Model):
        related = models.ForeignKey('Model3')

        def get_dependencies(self):
            return {'related__a', 'related__b', 'related__c'}

    def setUp(self):
        super(ValidationModelMixinTestCase, self).setUp()
        self.model1 = self.Model1()
        self.model2 = self.Model2()
        self.model3 = self.Model3()
        self.model4 = self.Model4()
        self.model4.related = self.model3

    def test_mixin_worked(self):
        self.assertFalse(hasattr(self.model1, 'validate'))
        self.assertTrue(hasattr(self.model2, 'validate'))
        self.assertTrue(hasattr(self.model3, 'validate'))

    def test_not_impl_error(self):
        with self.assertRaises(NotImplementedError):
            self.model2.get_dependencies()

    def test_validate_all_invalid(self):
        expected = {'warnings': {'a': ['Field "a" is required'],
                                 'b': ['Field "b" is required'],
                                 'c': ['Field "c" is required']}}
        self.assertEqual(expected, self.model3.validate())

    def test_validate_partial_invalid(self):
        self.model3.a = 'a'
        self.model3.b = 'b'

        expected = {'warnings': { 'c': ['Field "c" is required']}}
        self.assertEqual(expected, self.model3.validate())

    def test_validate_none_invalid(self):
        self.model3.a = 'a'
        self.model3.b = 'b'
        self.model3.c = 'c'

        expected = {'warnings': {}}
        self.assertEqual(expected, self.model3.validate())

    def test_validate_nested_invalid(self):
        expected = {'warnings': {'related': {'a': ['Field "a" is required'], 'c': ['Field "c" is required'], 'b': ['Field "b" is required']}}}

        self.assertEqual(expected, self.model4.validate())


class CloneModelsTestCaseMixin(object):
    def _check_model_fields(
        self, Model, obj, new_obj,
        non_equal_fields, equal_fields, check_not_None=False
    ):
        all_fields = non_equal_fields + equal_fields
        self._check_model_fields_keys(Model, all_fields)

        for field in non_equal_fields:
            if check_not_None:
                self.assertNotEqual(getattr(new_obj, field), None)
            self.assertNotEqual(getattr(obj, field), getattr(new_obj, field))

        for field in equal_fields:
            if check_not_None:
                self.assertNotEqual(getattr(new_obj, field), None, field)
            self.assertEqual(getattr(obj, field), getattr(new_obj, field))

    def _check_model_fields_keys(self, Model, expected_fields):
        """
        This is a bit tedious but it's just to make sure that when fields are
        added or removed from a model, the developer updates the cloning logic
        of the related model if necessary.

        Each object which extends CloneModelMixin has a `cloning_config`.
        Just make sure that it's configured properly.
        """
        actual_fields = [field.name for field in Model._meta.fields]
        remoded_fields = set(expected_fields) - set(actual_fields)
        added_fields = set(actual_fields) - set(expected_fields)

        text = ''
        if added_fields:
            text = ('It seems like you have added some fields "%s". '
                'This model gets cloned by the split case logic so now it\'s '
                'up to you do decide it these new fields have to be cloned, reset '
                'or just referenced. \n'
                'In order to do this, you need to look for the `cloning_config` of the model: \n'
                '1. if it\'s a fk and you want to create a new copy (with new id), add it to the '
                'clone_fks. Otherwise, if you want to reference the same copy, don\'t do anything'
                '2. if you want to exclude it (the default value will be used '
                'in the cloned object), add it to the `excludes`\n'
                '3. if you want to use a different value in your cloned version, you need to populate'
                'the `override_values` dinamically.\n'
                'After done this, just add the new field to the list of expected fields '
                'in this test and you\'re done! \n'
                % list(added_fields))
        elif remoded_fields:
            text = ('It seems like you have removed some fields "%s" from your model. '
                'All fine but just double-check that nothing is missing when cloning this '
                'model by the split case logic. That means, double check the `cloning_config`'
                'of your model.\n'
                'After done this, just remove the old field from the list of expected fields '
                'in this test and you\'re done!' % list(remoded_fields))

        self.assertFalse(text, text)


class CloneModelsTestCase(CloneModelsTestCaseMixin, TestCase):
    def _test_clone(self, Model, instance_creator, non_equal_fields, equal_fields):
        self.assertEqual(Model.objects.count(), 0)

        self.obj = instance_creator()
        self.cloned_obj = Model.clone_from_obj(self.obj.pk)

        self.assertEqual(Model.objects.count(), 2)

        self._check_model_fields(
            Model, self.obj, self.cloned_obj,
            non_equal_fields, equal_fields
        )

    def test_clone_savings(self):
        self._test_clone(
            Model=Savings,
            instance_creator=lambda: make_recipe(
                'legalaid.savings',
                bank_balance=100,
                investment_balance=200,
                asset_balance=300,
                credit_balance=400
            ),
            non_equal_fields=['id', 'created', 'modified'],
            equal_fields=[
                'bank_balance', 'investment_balance',
                'asset_balance', 'credit_balance'
            ]
        )

    def test_clone_income(self):
        self._test_clone(
            Model=Income,
            instance_creator=lambda: make_recipe(
                'legalaid.income',
                self_employed=True
            ),
            non_equal_fields=['id', 'created', 'modified'],
            equal_fields=[
                'earnings_interval_period', 'earnings_per_interval_value', 'earnings',
                'other_income_interval_period', 'other_income_per_interval_value', 'other_income',
                'self_employment_drawings', 'self_employment_drawings_per_interval_value', 'self_employment_drawings_interval_period',
                'tax_credits', 'tax_credits_interval_period', 'tax_credits_per_interval_value',
                'maintenance_received', 'maintenance_received_interval_period', 'maintenance_received_per_interval_value',
                'benefits', 'benefits_interval_period', 'benefits_per_interval_value',
                'child_benefits', 'child_benefits_interval_period', 'child_benefits_per_interval_value',
                'pension', 'pension_per_interval_value', 'pension_interval_period',
                'self_employed'
            ]
        )

    def test_clone_deductions(self):
        self._test_clone(
            Model=Deductions,
            instance_creator=lambda: make_recipe(
                'legalaid.deductions',
                criminal_legalaid_contributions=100
            ),
            non_equal_fields=['id', 'created', 'modified'],
            equal_fields=[
                'income_tax_interval_period', 'income_tax_per_interval_value', 'income_tax',
                'national_insurance_interval_period', 'national_insurance_per_interval_value', 'national_insurance',
                'maintenance_interval_period', 'maintenance_per_interval_value', 'maintenance',
                'childcare_interval_period', 'childcare_per_interval_value', 'childcare',
                'mortgage_interval_period', 'mortgage_per_interval_value', 'mortgage',
                'rent_interval_period', 'rent_per_interval_value', 'rent',
                'criminal_legalaid_contributions'
            ]
        )

    def test_clone_personal_details(self):
        self._test_clone(
            Model=PersonalDetails,
            instance_creator=lambda: make_recipe(
                'legalaid.personal_details',
                title='Title',
                full_name='Full name',
                postcode='Postcode',
                street='Street',
                mobile_phone='Mobile phone',
                home_phone='Home phone',
                email='email@email.com',
                date_of_birth=datetime.date(day=1, month=1, year=2000),
                ni_number='ni number',
                contact_for_research=True,
                vulnerable_user=True,
                safe_to_contact=CONTACT_SAFETY.SAFE,
                case_count=2
            ),
            non_equal_fields=['id', 'created', 'modified', 'reference', 'case_count'],
            equal_fields=[
                'title', 'full_name', 'postcode', 'street', 'mobile_phone',
                'home_phone', 'email', 'date_of_birth', 'ni_number',
                'contact_for_research', 'vulnerable_user', 'safe_to_contact',
                'safe_to_email', 'diversity', 'diversity_modified'
            ]
        )

    def test_clone_third_party(self):
        self._test_clone(
            Model=ThirdPartyDetails,
            instance_creator=lambda: make_recipe(
                'legalaid.thirdparty_details',
                pass_phrase='Pass phrase',
                reason=THIRDPARTY_REASON[0][0],
                personal_relationship=THIRDPARTY_RELATIONSHIP[0][0],
                personal_relationship_note='Relationship Notes',
                spoke_to=True,
                no_contact_reason='No Contact Reason',
                organisation_name='Organisation Name'
            ),
            non_equal_fields=['id', 'created', 'modified', 'reference', 'personal_details'],
            equal_fields=[
                'pass_phrase', 'reason', 'personal_relationship', 'personal_relationship_note',
                'spoke_to', 'no_contact_reason', 'organisation_name'
            ]
        )

    def test_clone_adaptations(self):
        self._test_clone(
            Model=AdaptationDetails,
            instance_creator=lambda: make_recipe(
                'legalaid.adaptation_details',
                bsl_webcam=True,
                minicom=True,
                text_relay=True,
                skype_webcam=True,
                language=ADAPTATION_LANGUAGES[0][0],
                notes='Notes',
                callback_preference=True
            ),
            non_equal_fields=['id', 'created', 'modified', 'reference'],
            equal_fields=[
                'bsl_webcam', 'minicom', 'text_relay', 'skype_webcam',
                'language', 'notes', 'callback_preference'
            ]
        )

    def test_clone_person(self):
        self._test_clone(
            Model=Person,
            instance_creator=lambda: make_recipe(
                'legalaid.full_person'
            ),
            non_equal_fields=['id', 'created', 'modified', 'income', 'savings', 'deductions'],
            equal_fields=[]
        )


class SplitCaseTestCase(CloneModelsTestCaseMixin, TestCase):
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
        super(SplitCaseTestCase, self).setUp()

        self.cat1_data = self.build_category_data()
        self.cat2_data = self.build_category_data()

        self.user = make_user()

    def assertDiagnosis(self, diagnosis, category):
        self.assertTrue(diagnosis)
        self.assertEqual(diagnosis.state, DIAGNOSIS_SCOPE.INSCOPE)
        self.assertEqual(diagnosis.category, category)

    def assertPersonalDetails(self, pd, new_pd):
        self.assertEqual(pd, new_pd)

        self.assertEqual(
            PersonalDetails.objects.get(pk=pd.pk).case_count, 2
        )

    def assertEligibilityCheck(self, ec, new_ec, category):
        self._check_model_fields(
            EligibilityCheck, ec, new_ec,
            non_equal_fields=[
                'id', 'modified', 'created', 'reference', 'category',
                'you', 'partner', 'disputed_savings'
            ],
            equal_fields=[
                'your_problem_notes', 'notes', 'state', 'dependants_young',
                'dependants_old', 'on_passported_benefits', 'on_nass_benefits',
                'is_you_or_your_partner_over_60', 'has_partner', 'calculations'
            ],
            check_not_None=True
        )

        self.assertEqual(new_ec.category, category)

        props = list(ec.property_set.all())
        new_props = list(new_ec.property_set.all())
        self.assertEqual(len(props), len(new_props))
        self.assertTrue(len(new_props) > 0)
        for prop, new_prop in zip(props, new_props):
            self.assertProperty(prop, new_prop)

    def assertProperty(self, prop, new_prop):
        self._check_model_fields(
            Property, prop, new_prop,
            non_equal_fields=['id', 'created', 'modified', 'eligibility_check'],
            equal_fields=['value', 'mortgage_left', 'share', 'disputed', 'main'],
            check_not_None=True
        )

    def assertAlternativeHelpArticles(self, case, new_case):
        kas = list(case.caseknowledgebaseassignment_set.all())
        new_kas = list(new_case.caseknowledgebaseassignment_set.all())
        self.assertEqual(len(kas), len(new_kas))
        self.assertTrue(len(new_kas) > 0)
        for ka, new_ka in zip(kas, new_kas):
            self.assertNotEqual(ka.case, new_ka.case)
            self.assertEqual(ka.alternative_help_article, new_ka.alternative_help_article)
            self.assertNotEqual(new_ka.alternative_help_article, None)
            self.assertEqual(ka.assigned_by, new_ka.assigned_by)
            self.assertNotEqual(new_ka.assigned_by, None)

    def test_split_bare_minimum_case(self):
        case = make_recipe('legalaid.empty_case')

        new_case = case.split(
            user=self.user,
            category=self.cat2_data.category,
            matter_type1=self.cat2_data.matter_type1,
            matter_type2=self.cat2_data.matter_type2,
            assignment_internal=False
        )

        self.assertNotEqual(case.reference, new_case.reference)
        self.assertDiagnosis(new_case.diagnosis, self.cat2_data.category)
        self.assertEqual(case.personal_details, None)
        self.assertEqual(new_case.created_by, self.user)
        self.assertEqual(new_case.requires_action_by, REQUIRES_ACTION_BY.OPERATOR)
        self.assertEqual(new_case.notes, '')
        self.assertEqual(new_case.provider_notes, '')
        self.assertNotEqual(case.laa_reference, new_case.laa_reference)
        self.assertEqual(new_case.billable_time, 0)
        self.assertEqual(new_case.matter_type1, self.cat2_data.matter_type1)
        self.assertEqual(new_case.matter_type2, self.cat2_data.matter_type2)
        self.assertEqual(new_case.alternative_help_articles.count(), 0)

        for field in [
            'eligibility_check', 'locked_by', 'locked_at', 'provider',
            'thirdparty_details', 'adaptation_details', 'media_code',
            'outcome_code', 'level', 'exempt_user', 'exempt_user_reason',
            'ecf_statement'
        ]:
            self.assertEqual(getattr(new_case, field), None)

    def _test_split_full_case(self, internal):
        case = get_full_case(
            self.cat1_data.matter_type1,
            self.cat1_data.matter_type2
        )
        CaseKnowledgebaseAssignment.objects.create(
            case=case, assigned_by=make_user(),
            alternative_help_article=make_recipe('knowledgebase.article')
        )

        new_case = case.split(
            user=self.user,
            category=self.cat2_data.category,
            matter_type1=self.cat2_data.matter_type1,
            matter_type2=self.cat2_data.matter_type2,
            assignment_internal=internal
        )

        non_equal_fields = [
            'id', 'created', 'modified', 'eligibility_check', 'diagnosis',
            'created_by', 'locked_by', 'locked_at', 'thirdparty_details',
            'adaptation_details', 'billable_time', 'matter_type1', 'matter_type2',
            'outcome_code', 'level', 'reference', 'laa_reference', 'from_case',
            'outcome_code_id', 'requires_action_at', 'callback_attempt'
        ]
        equal_fields = [
            'personal_details', 'notes', 'provider_notes', 'media_code',
            'exempt_user', 'exempt_user_reason', 'ecf_statement',
            'provider_viewed', 'source'
        ]

        if internal:
            equal_fields += ['provider', 'requires_action_by']
        else:
            non_equal_fields += ['provider', 'requires_action_by']

        self._check_model_fields(
            Case, case, new_case, non_equal_fields, equal_fields
        )

        self.assertEligibilityCheck(
            case.eligibility_check, new_case.eligibility_check,
            self.cat2_data.category
        )
        self.assertDiagnosis(new_case.diagnosis, self.cat2_data.category)
        self.assertPersonalDetails(case.personal_details, new_case.personal_details)
        self.assertAlternativeHelpArticles(case, new_case)

        for field in ['eligibility_check', 'diagnosis', 'thirdparty_details', 'adaptation_details']:
            self.assertNotEqual(getattr(new_case, field), None)
            self.assertNotEqual(getattr(case, field), getattr(new_case, field))

        expected_values = {
            'created_by': self.user,
            'locked_by': None,
            'locked_at': None,
            'billable_time': 0,
            'matter_type1': self.cat2_data.matter_type1,
            'matter_type2': self.cat2_data.matter_type2,
            'outcome_code': None,
            'outcome_code_id': None,
            'level': None,
            'requires_action_at': None,
            'callback_attempt': 0,

            # it should keep these values from the original case
            'notes': case.notes,
            'provider_notes': case.provider_notes,
            'media_code': case.media_code,
            'source': case.source,
            'exempt_user': case.exempt_user,
            'exempt_user_reason': case.exempt_user_reason,
            'ecf_statement': case.ecf_statement,
            'personal_details': case.personal_details,
            'from_case': case
        }

        if internal:
            expected_values.update({
                'requires_action_by': case.requires_action_by,
                'provider': case.provider,
            })
        else:
            expected_values.update({
                'requires_action_by': REQUIRES_ACTION_BY.OPERATOR,
                'provider': None,
            })

        for field, value in expected_values.items():
            self.assertEqual(getattr(new_case, field), value)

    def test_split_full_case_internal_assignment(self):
        self._test_split_full_case(internal=True)

    def test_split_full_case_external_assignment(self):
        self._test_split_full_case(internal=False)
