from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase

from core.tests.test_base import CLAProviderAuthBaseApiTestMixin, make_recipe

from legalaid.models import Property


class EligibilityCheckTests(CLAProviderAuthBaseApiTestMixin, APITestCase):

    def setUp(self):
        super(EligibilityCheckTests, self).setUp()

        self.check = make_recipe('legalaid.tests.eligibility_check')
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
             'on_nass_benefits',
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
        make_recipe('legalaid.tests.property', eligibility_check=self.check, _quantity=4)

        # making extra properties
        make_recipe('legalaid.tests.property', eligibility_check=self.check, _quantity=5)

        self.assertEqual(Property.objects.count(), 9)

        response = self.client.get(self.detail_url, format='json',
                                   HTTP_AUTHORIZATION='Bearer %s' % self.token)
        self.assertEligibilityCheckResponseKeys(response)
        self.assertEligibilityCheckEqual(response.data, self.check)
