from django.test import TestCase
from django.conf import settings

from model_mommy import mommy

from legalaid.models import CaseOutcome

from ..forms import ProviderAllocationForm


def make_recipe(model_name, **kwargs):
    return mommy.make_recipe('legalaid.tests.%s' % model_name, **kwargs)


def cla_provider_make_recipe(model_name, **kwargs):
    return mommy.make_recipe('cla_provider.tests.%s' % model_name, **kwargs)


class ProviderAllocationFormTestCase(TestCase):
    def test_save(self):
        outcome_codes = make_recipe('outcome_code', _quantity=2)
        case = make_recipe('case')
        user = mommy.make(settings.AUTH_USER_MODEL)
        provider = cla_provider_make_recipe('provider', active=True)

        form = ProviderAllocationForm(data={
            'outcome_code': outcome_codes[0].code,
            'outcome_notes': 'lorem ipsum',
            'provider': provider.pk
        })

        self.assertTrue(form.is_valid())
        self.assertEqual(CaseOutcome.objects.count(), 0)

        form.save(case, user)

        self.assertEqual(CaseOutcome.objects.count(), 1)
        self.assertEqual(CaseOutcome.objects.all()[0].case, case)
        self.assertEqual(case.provider, provider)

    def test_save_inactive_provider(self):
        outcome_codes = make_recipe('outcome_code', _quantity=2)
        provider = cla_provider_make_recipe('provider', active=False)

        form = ProviderAllocationForm(data={
            'outcome_code': outcome_codes[0].code,
            'outcome_notes': 'lorem ipsum',
            'provider': provider.pk
        })

        self.assertFalse(form.is_valid())
        self.assertDictEqual(form.errors,
            {'provider': [u'Select a valid choice. That choice is not one of the available choices.']}
        )
