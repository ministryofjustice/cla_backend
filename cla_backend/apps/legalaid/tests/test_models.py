from django.test import TestCase

from model_mommy import mommy, recipe

from eligibility_calculator.models import CaseData
from model_mommy.recipe import foreign_key

from ..models import EligibilityCheck


def make_recipe(model_name, **kwargs):
    return mommy.make_recipe('legalaid.tests.%s' % model_name, **kwargs)


class EligibilityCheckTestCase(TestCase):
    def test_to_case_data_fail_without_your_finances(self):
        """
        Should fail as your_finances object is always needed
        """
        check = EligibilityCheck()

        self.assertRaises(ValueError, check.to_case_data)

    def assertCaseDataEqual(self, obj1, obj2):
        for prop in CaseData.PROPERTY_SET:
            if hasattr(obj1, prop) or hasattr(obj2, prop):
                val1 = getattr(obj1, prop)
                val2 = getattr(obj2, prop)

                assertFunc = self.assertEqual
                if isinstance(val1, list) or isinstance(val2, list):
                    assertFunc = self.assertItemsEqual

                assertFunc(val1, val2, u"%s: %s != %s" % (prop, val1, val2))

    def test_to_case_data_without_partner(self):
        """
        EligibilityCheck partner data won't be used during CaseData creation
        """
        check = make_recipe('eligibility_check',
            category=make_recipe('category', code='code'),
            you=make_recipe('person'),
            # your_finances=make_recipe('finance',
            #     bank_balance=100, investment_balance=200,
            #     asset_balance=300, credit_balance=400,
            #     earnings=500, other_income=600,
            #     self_employed=True, income_tax_and_ni=700,
            #     maintenance=710, mortgage_or_rent=720,
            #     criminal_legalaid_contributions=730
            # ),
            dependants_young=3, dependants_old=2,
            is_you_or_your_partner_over_60=True,
            on_passported_benefits=True,
            has_partner=False,
        )

        case_data = check.to_case_data()
        self.assertCaseDataEqual(case_data, CaseData(
            category='code', dependant_children=5, savings=100, investments=200,
            money_owed=400, valuable_items=300, earnings=500, other_income=600,
            self_employed=True, property_data=[], is_you_or_your_partner_over_60=True,
            has_partner=False, is_partner_opponent=False, income_tax_and_ni=700,
            maintenance=710, mortgage_or_rent=720,
            criminal_legalaid_contributions=730,
            on_passported_benefits=True
        ))

    def test_to_case_data_with_partner(self):
        """
        EligibilityCheck partner data is used during CaseData creation
        """
        check = make_recipe('eligibility_check',
            category=make_recipe('category', code='code'),
            you= make_recipe('person',
                            income=make_recipe('income',
                                        earnings=500,
                                        other_income=600,
                                        self_employed=True
                            )
            ),
            partner=
            make_recipe('person',
                        income= make_recipe('income',
                                            earnings=0,
                                            other_income=0
                        ),

                        savings= make_recipe('savings',
                                             bank_balance=101,
                                             investment_balance=201,
                                             asset_balance=301,
                                             credit_balance=401,
                                             )

            ),
            # your_finances=make_recipe('finance',
            #     bank_balance=100, investment_balance=200,
            #     asset_balance=300, credit_balance=400,
            #     earnings=500, other_income=600,
            #     self_employed=True, income_tax_and_ni=700,
            #     maintenance=710, mortgage_or_rent=720,
            #     criminal_legalaid_contributions=730
            # ),
            # partner_finances=make_recipe('finance',
            #     bank_balance=101, investment_balance=201,
            #     asset_balance=301, credit_balance=401,
            #     earnings=501, other_income=601,
            #     self_employed=True
            # ),
            dependants_young=3, dependants_old=2,
            is_you_or_your_partner_over_60=True,
            on_passported_benefits=True,
            has_partner=True,
        )

        case_data = check.to_case_data()
        self.assertCaseDataEqual(case_data, CaseData(
            category='code', dependant_children=5, savings=100, investments=200,
            money_owed=400, valuable_items=300, earnings=500, other_income=600,
            self_employed=True, property_data=[], is_you_or_your_partner_over_60=True,
            has_partner=True, is_partner_opponent=False, income_tax_and_ni=700,
            partner_savings=101, partner_investments=201, partner_money_owed=401,
            partner_valuable_items=301, partner_earnings=501, partner_other_income=601,
            partner_self_employed=True,
            maintenance=710, mortgage_or_rent=720,
            criminal_legalaid_contributions=730,
            on_passported_benefits=True,
        ))

    def test_to_case_data_with_properties(self):
        """
        Tests with non-empty property set
        """
        check = make_recipe('eligibility_check',
            category=make_recipe('category', code='code'),
            your_finances=make_recipe('finance',
                bank_balance=100, investment_balance=200,
                asset_balance=300, credit_balance=400,
                earnings=500, other_income=600,
                self_employed=True, income_tax_and_ni=700,
                maintenance=710, mortgage_or_rent=720,
                criminal_legalaid_contributions=730
            ),
            dependants_young=3, dependants_old=2,
            is_you_or_your_partner_over_60=True,
            on_passported_benefits=True,
            has_partner=False,
        )
        make_recipe('property',
            eligibility_check=check,
            value=recipe.seq(30), mortgage_left=recipe.seq(40),
            share=recipe.seq(50), _quantity=3
        )

        case_data = check.to_case_data()
        self.assertCaseDataEqual(case_data, CaseData(
            category='code', dependant_children=5, savings=100, investments=200,
            money_owed=400, valuable_items=300, earnings=500, other_income=600,
            self_employed=True, property_data=[(31, 41, 51), (32, 42, 52), (33, 43, 53)],
            is_you_or_your_partner_over_60=True,
            has_partner=False, is_partner_opponent=False, income_tax_and_ni=700,
            maintenance=710, mortgage_or_rent=720,
            criminal_legalaid_contributions=730,
            on_passported_benefits=True
        ))
