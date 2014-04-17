import copy
import uuid
from cla_provider.serializers import CaseSerializer, EligibilityCheckSerializer
from cla_common.constants import CASE_STATE_OPEN, CASE_STATE_CLOSED
import mock

from model_mommy import mommy

from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from eligibility_calculator.exceptions import PropertyExpectedException

from legalaid.models import Category, EligibilityCheck, Property, \
    Case, PersonalDetails, Person, Income, Savings

from core.tests.test_base import CLAProviderAuthBaseApiTestMixin


def make_recipe(model_name, **kwargs):
    return mommy.make_recipe('legalaid.tests.%s' % model_name, **kwargs)


def cla_provider_make_recipe(model_name, **kwargs):
    return mommy.make_recipe('cla_provider.tests.%s' % model_name, **kwargs)


class CategoryTests(CLAProviderAuthBaseApiTestMixin, APITestCase):
    def setUp(self):
        super(CategoryTests, self).setUp()

        self.categories = make_recipe('category', _quantity=3)

        self.list_url = reverse('cla_provider:category-list')
        self.detail_url = reverse(
            'cla_provider:category-detail', args=(),
            kwargs={'code': self.categories[0].code}
        )

    def test_get_allowed(self):
        """
        Ensure we can GET the list and it is ordered
        """
        # LIST
        response = self.client.get(self.list_url,
                                   HTTP_AUTHORIZATION='Bearer %s' % self.token,
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([d['name'] for d in response.data], ['Name1', 'Name2', 'Name3'])

        # DETAIL
        response = self.client.get(self.detail_url,
                                   HTTP_AUTHORIZATION='Bearer %s' % self.token,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Name1')

    def test_methods_not_allowed(self):
        """
        Ensure that we can't POST, PUT or DELETE
        """

        ### LIST
        self._test_post_not_allowed(self.list_url)
        self._test_put_not_allowed(self.list_url)
        self._test_delete_not_allowed(self.list_url)

        ### DETAIL
        self._test_post_not_allowed(self.detail_url)
        self._test_put_not_allowed(self.detail_url)
        self._test_delete_not_allowed(self.detail_url)


    def test_methods_not_authorized(self):
        ### LIST
        self._test_post_not_authorized(self.list_url, self.operator_token)
        self._test_put_not_authorized(self.list_url, self.operator_token)
        self._test_delete_not_authorized(self.list_url, self.operator_token)

        ### DETAIL
        self._test_post_not_authorized(self.detail_url, self.operator_token)
        self._test_put_not_authorized(self.detail_url, self.operator_token)
        self._test_delete_not_authorized(self.detail_url, self.operator_token)

class EligibilityCheckTests(CLAProviderAuthBaseApiTestMixin, APITestCase):

    def setUp(self):
        super(EligibilityCheckTests, self).setUp()

        self.check = make_recipe('eligibility_check')
        self.detail_url = reverse(
            'cla_provider:eligibility_check-detail', args=(),
            kwargs={'reference': self.check.reference}
        )


    def assertEligibilityCheckResponseKeys(self, response):
        self.assertItemsEqual(
            response.data.keys(),
            ['reference',
             'category',
             'notes',
             'your_problem_notes',
             'property_set',
             'dependants_young',
             'dependants_old',
             'you',
             'partner',
             'has_partner',
             'on_passported_benefits',
             'is_you_or_your_partner_over_60',
             'state']
        )

    def assertSavingsEqual(self, data, obj):
        if obj is None or data is None:
            self.assertEqual(obj, data)
            return

        for prop in [
            'bank_balance', 'investment_balance',
            'asset_balance', 'credit_balance'
        ]:
            self.assertEqual(getattr(obj, prop), data.get(prop))

    def assertIncomeEqual(self, data, obj):
        if obj is None or data is None:
            self.assertEqual(obj, data)
            return

    def assertDeductionsEqual(self, data, obj):
        if obj is None or data is None:
            self.assertEqual(obj, data)
            return

        for prop in [
            'income_tax_and_ni', 'maintenance', 'childcare',
            'mortgage_or_rent', 'criminal_legalaid_contributions'
        ]:
            self.assertEqual(getattr(obj, prop), data.get(prop))

    def assertFinanceEqual(self, data, obj):
        if data is None or obj is None:
            self.assertEqual(data, obj)
            return

        o_income = getattr(obj, 'income')
        d_income = data.get('income')
        self.assertIncomeEqual(d_income, o_income)

        o_savings = getattr(obj, 'savings')
        d_savings = data.get('savings')
        self.assertSavingsEqual(d_savings, o_savings)

        o_deductions = getattr(obj, 'deductions')
        d_deductions = data.get('deductions')
        self.assertDeductionsEqual(d_deductions, o_deductions)

    def get_is_eligible_url(self, reference):
        return reverse(
            'call_centre:eligibility_check-is-eligible',
            args=(),
            kwargs={'reference': unicode(reference)}
        )

    def assertEligibilityCheckEqual(self, data, check):
        self.assertEqual(data['reference'], unicode(check.reference))
        self.assertEqual(data['category'], check.category.code if check.category else None)
        self.assertEqual(data['your_problem_notes'], check.your_problem_notes)
        self.assertEqual(data['notes'], check.notes)
        self.assertEqual(len(data['property_set']), check.property_set.count())
        self.assertEqual(data['dependants_young'], check.dependants_young)
        self.assertEqual(data['dependants_old'], check.dependants_old)
        self.assertFinanceEqual(data['you'], check.you)
        self.assertFinanceEqual(data['partner'], check.partner)

    def test_methods_not_allowed(self):
        """
        Ensure that we can't POST, PUT or DELETE
        """
        ### DETAIL
        self._test_post_not_allowed(self.detail_url)
        self._test_delete_not_allowed(self.detail_url)


    def test_get_object(self):
        """
        GET should not return properties of other eligibility check objects
        """
        make_recipe('property', eligibility_check=self.check, _quantity=4)

        # making extra properties
        make_recipe('property', eligibility_check=self.check, _quantity=5)

        self.assertEqual(Property.objects.count(), 9)

        response = self.client.get(self.detail_url, format='json',
                                   HTTP_AUTHORIZATION='Bearer %s' % self.token)
        self.assertEligibilityCheckResponseKeys(response)
        self.assertEligibilityCheckEqual(response.data, self.check)



class CaseTests(CLAProviderAuthBaseApiTestMixin, APITestCase):
    def setUp(self):
        super(CaseTests, self).setUp()
        self.case_obj = make_recipe('case', provider=self.staff.provider)
        self.list_url = reverse('cla_provider:case-list')
        obj = make_recipe('case')
        self.detail_url = reverse(
            'cla_provider:case-detail', args=(),
            kwargs={'reference': obj.reference}
        )

    def assertCaseCheckResponseKeys(self, response):
        self.assertItemsEqual(
            response.data.keys(),
            ['eligibility_check', 'personal_details', 'reference',
             'created', 'modified', 'state', 'created_by',
             'provider', 'locked_by']
        )

    def assertPersonalDetailsEqual(self, data, obj):
        if data is None or obj is None:
            self.assertEqual(data, obj)
        else:
            for prop in ['title', 'full_name', 'postcode', 'street', 'town', 'mobile_phone', 'home_phone']:
                self.assertEqual(getattr(obj, prop), data[prop])

    def assertCaseEqual(self, data, case):
        self.assertEqual(case.reference, data['reference'])
        self.assertEqual(unicode(case.eligibility_check.reference), data['eligibility_check'])
        self.assertPersonalDetailsEqual(data['personal_details'], case.personal_details)

    def test_methods_not_allowed(self):
        """
        Ensure that we can't POST, PUT or DELETE
        """
        ### LIST
        self._test_delete_not_allowed(self.list_url)

        ### DETAIL
        self._test_delete_not_allowed(self.detail_url)

        ### CREATE
        self._test_post_not_allowed(self.list_url)

    def test_get_allowed(self):
        """
        Ensure we can GET the list and it is ordered
        """
        # LIST
        response = self.client.get(self.list_url,
                                   HTTP_AUTHORIZATION='Bearer %s' % self.token,
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)


#     def test_locked_by_when_getting_case(self):
#         """
#         After each detail GET, the locked_by gets set to the logged in User.
#         """
#         self.assertEqual(self.case_obj.locked_by, None)
#         response = self.client.get(
#             self.detail_url, HTTP_AUTHORIZATION='Bearer %s' % self.token,
#             format='json'
#         )
#  
#         self.assertEqual(response.data['locked_by'], 'john')
#         case = Case.objects.get(pk=self.case_obj.pk)
#         self.assertEqual(case.locked_by.username, 'john')
#         self.assertCaseCheckResponseKeys(response)

