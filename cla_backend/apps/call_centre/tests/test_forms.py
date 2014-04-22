from django.test import TestCase
from django.conf import settings

from model_mommy import mommy

from cla_common.constants import CASE_STATE_OPEN, CASE_STATE_CLOSED

from ..forms import ProviderAllocationForm, CloseCaseForm


def make_recipe(model_name, **kwargs):
    return mommy.make_recipe('legalaid.tests.%s' % model_name, **kwargs)


def cla_provider_make_recipe(model_name, **kwargs):
    return mommy.make_recipe('cla_provider.tests.%s' % model_name, **kwargs)


class ProviderAllocationFormTestCase(TestCase):
    def test_save(self):
        case = make_recipe('case')
        user = mommy.make(settings.AUTH_USER_MODEL)
        provider = cla_provider_make_recipe('provider', active=True)

        form = ProviderAllocationForm(data={
            'provider': provider.pk
        })

        self.assertTrue(form.is_valid())

        form.save(case, user)

        self.assertEqual(case.provider, provider)

    def test_save_inactive_provider(self):
        provider = cla_provider_make_recipe('provider', active=False)

        form = ProviderAllocationForm(data={
            'provider': provider.pk
        })

        self.assertFalse(form.is_valid())
        self.assertDictEqual(form.errors,
            {'provider': [u'Select a valid choice. That choice is not one of the available choices.']}
        )


class CloseCaseFormTestCase(TestCase):
    def test_save(self):
        user = mommy.make(settings.AUTH_USER_MODEL)
        case = make_recipe('case', state=CASE_STATE_OPEN)

        form = CloseCaseForm(data={})

        self.assertTrue(form.is_valid())

        form.save(case, user)

        self.assertEqual(case.state, CASE_STATE_CLOSED)
