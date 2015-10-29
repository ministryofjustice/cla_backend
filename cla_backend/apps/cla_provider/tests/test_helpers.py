from collections import defaultdict
import datetime
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
import mock

from cla_provider.models import ProviderAllocation
from legalaid.models import Case

from core.tests.mommy_utils import make_recipe

from cla_provider.helpers import ProviderAllocationHelper, \
    ProviderDistributionHelper


class ProviderAllocationHelperTestCase(TestCase):
    def build_providers(self, providers_data):
        providers = []
        for id, pa in providers_data.items():
            providers.append(
                mock.MagicMock(
                    provider=mock.MagicMock(id=id),
                    weighted_distribution=pa['weight']
                )
            )
        return providers

    def _test__get_random_provider(self, alloc_data, num_iterations=100000):
        # print "\n\nNew test"
        helper = ProviderAllocationHelper()
        helper._providers_in_category = self.build_providers(alloc_data)

        results = defaultdict(int)
        category = mock.MagicMock()
        for i in range(0, num_iterations):
            winner = helper._get_random_provider(category)
            results[winner.id] += 1

        for id, count in results.items():
            prob = (count * 100.) / num_iterations
            # print 'expected %s - found %s. Difference %s' % (
            #     alloc_data[id]['expected_prob'], prob,
            #     ((alloc_data[id]['expected_prob'] * 0.01) * num_iterations) - \
            #     ((prob * 0.01) * num_iterations)
            # )
            self.assertAlmostEqual(prob, alloc_data[id]['expected_prob'], delta=1.5)

    def test__get_random_provider(self):
        # weight as integers
        self._test__get_random_provider({
            20: {'weight': 20, 'expected_prob': 20},
            30: {'weight': 30, 'expected_prob': 30},
            50: {'weight': 50, 'expected_prob': 50},
        })

        # weight as floats
        self._test__get_random_provider({
            28: {'weight': 2.8, 'expected_prob': 28},
            27: {'weight': 2.7, 'expected_prob': 27},
            4: {'weight': 0.4, 'expected_prob': 4},
            5: {'weight': 0.5, 'expected_prob': 5},
            13: {'weight': 1.3, 'expected_prob': 13},
            1: {'weight': 0.1, 'expected_prob': 1},
            10: {'weight': 1., 'expected_prob': 10},
            12: {'weight': 1.2, 'expected_prob': 12},
        })

        # 2 items
        self._test__get_random_provider({
            1: {'weight': 1, 'expected_prob': 1},
            99: {'weight': 99, 'expected_prob': 99},
        })

        # # same weight
        self._test__get_random_provider({
            1: {'weight': 0.8, 'expected_prob': 33.3},
            2: {'weight': 0.8, 'expected_prob': 33.3},
            3: {'weight': 0.8, 'expected_prob': 33.3},
        })

        # 0 weight
        self._test__get_random_provider({
            0: {'weight': 0, 'expected_prob': 0},
            100: {'weight': 2, 'expected_prob': 100},
        })

    @mock.patch('cla_provider.helpers.ProviderAllocation')
    def test__get_random_provider_with_empty_list(self, MockedProviderAllocation):
        MockedProviderAllocation.objects.filter.return_value = []

        helper = ProviderAllocationHelper()

        winner = helper._get_random_provider(mock.MagicMock())
        self.assertEqual(winner, None)

    def test_get_qualifying_providers(self):
        category1 = make_recipe('legalaid.category')
        category2 = make_recipe('legalaid.category')

        cat1_provider1 = make_recipe('cla_provider.provider', active=True)
        make_recipe(
            'cla_provider.provider_allocation',
            weighted_distribution=0.5,
            provider=cat1_provider1,
            category=category1
        )

        cat1_provider2 = make_recipe('cla_provider.provider', active=True)
        make_recipe(
            'cla_provider.provider_allocation',
            weighted_distribution=0.5,
            provider=cat1_provider2,
            category=category1
        )

        cat2_provider1 = make_recipe('cla_provider.provider', active=True)
        make_recipe(
            'cla_provider.provider_allocation',
            weighted_distribution=0.5,
            provider=cat2_provider1,
            category=category2
        )

        helper = ProviderAllocationHelper()
        cat1_providers = helper.get_qualifying_providers(category1)
        self.assertItemsEqual(
            cat1_providers, [cat1_provider1, cat1_provider2]
        )

        # Set cat1_provider2.active == False => only one prov returned
        cat1_provider2.active = False
        cat1_provider2.save()

        helper = ProviderAllocationHelper()
        cat1_providers = helper.get_qualifying_providers(category1)
        self.assertItemsEqual(
            cat1_providers, [cat1_provider1]
        )

    def test_get_suggested_provider_random(self):

        as_of = timezone.make_aware(
            datetime.datetime(day=8, month=12, year=2014, hour=10, minute=0),
            timezone.get_current_timezone()
        )

        category = make_recipe('legalaid.category')

        provider = make_recipe('cla_provider.provider', active=True)
        make_recipe(
            'cla_provider.provider_allocation',
            weighted_distribution=0.5,
            provider=provider,
            category=category
        )

        helper = ProviderAllocationHelper(as_of=as_of)
        choosen_provider = helper._get_random_provider(category)
        self.assertEqual(choosen_provider, provider)

        # Set cat1_provider2.active == False => only one prov returned
        provider.active = False
        provider.save()

        helper = ProviderAllocationHelper(as_of=as_of)
        choosen_provider = helper.get_suggested_provider(category)
        self.assertEqual(choosen_provider, None)

    def test_get_suggested_provider_best_fit(self):
        # slightly brute force test

        as_of = timezone.make_aware(
            datetime.datetime(day=8, month=12, year=2014, hour=10, minute=0),
            timezone.get_current_timezone()
        )

        category = make_recipe('legalaid.category')

        provider1 = make_recipe('cla_provider.provider', active=True)
        provider2 = make_recipe('cla_provider.provider', active=True)
        make_recipe(
            'cla_provider.provider_allocation',
            weighted_distribution=0.5,
            provider=provider1,
            category=category,
        )
        make_recipe(
            'cla_provider.provider_allocation',
            weighted_distribution=1,
            provider=provider2,
            category=category,
        )
        ProviderAllocation.objects.update(modified=as_of-datetime.timedelta(days=1))

        helper = ProviderAllocationHelper(as_of=as_of)
        counts = {provider1: 0, provider2: 0}
        # quick sanity check that random allocation is working
        for i in range(100):
            sugg = helper.get_suggested_provider(category)
            counts[sugg] += 1
        self.assertTrue(counts[provider2] > counts[provider1])

        case1 = make_recipe('legalaid.eligible_case', diagnosis__category=category)
        case1.assign_to_provider(provider1)

        # cases assigned at != today are ignored, so expect same as before
        counts = {provider1: 0, provider2: 0}
        for i in range(100):
            sugg = helper.get_suggested_provider(category)
            counts[sugg] += 1
        self.assertTrue(counts[provider2] > counts[provider1])

        case1.provider_assigned_at = as_of
        case1.save()

        for i in range(100):
            self.assertEqual(helper.get_suggested_provider(category), provider2)
            # should always be provider 2

    def test_get_suggested_provider_rota(self):
        as_of = timezone.make_aware(
            datetime.datetime(day=7, month=12, year=2014, hour=10, minute=0),
            timezone.get_current_timezone()
        )

        category = make_recipe('legalaid.category')

        provider = make_recipe('cla_provider.provider', active=True)
        make_recipe(
            'cla_provider.outofhoursrota',
            provider=provider,
            start_date=as_of,
            end_date=as_of + datetime.timedelta(days=1),
            category=category
        )

        helper = ProviderAllocationHelper(as_of=as_of)
        choosen_provider = helper.get_suggested_provider(category)
        self.assertEqual(choosen_provider, provider)

        # Set cat1_provider2.active == False => only one prov returned
        provider.active = False
        provider.save()

        helper = ProviderAllocationHelper(as_of=as_of)
        choosen_provider = helper.get_suggested_provider(category)
        self.assertEqual(choosen_provider, None)

    def assertWithinAllowedAccuracy(self, expected, accuracy, n):
        diff = expected * accuracy
        if not expected - diff <= n <= expected + diff:
            raise self.failureException(
                'Expected: %s, Got: %s  - not within allowed accuracy: %s' %
                (expected, n, accuracy))

    def test_even_allocation(self):
        # Test the distribution of cases to {accuracy} accuracy over {total} cases
        total = 8000
        accuracy = Decimal('0.001')
        with mock.patch('cla_common.call_centre_availability.current_datetime', datetime.datetime(2015, 7, 7, 11, 59, 0)):
            helper = ProviderAllocationHelper()

            as_of = timezone.make_aware(
                datetime.datetime(day=7, month=7, year=2015, hour=12, minute=0),
                timezone.get_current_timezone()
            )

            category = make_recipe('legalaid.category')

            provider1 = make_recipe('cla_provider.provider', active=True)
            provider2 = make_recipe('cla_provider.provider', active=True)
            provider3 = make_recipe('cla_provider.provider', active=True)
            provider4 = make_recipe('cla_provider.provider', active=True)
            a1 = make_recipe(
                'cla_provider.provider_allocation',
                weighted_distribution=5,
                provider=provider1,
                category=category,
            )
            a2 = make_recipe(
                'cla_provider.provider_allocation',
                weighted_distribution=1,
                provider=provider2,
                category=category,
            )
            a3 = make_recipe(
                'cla_provider.provider_allocation',
                weighted_distribution=1,
                provider=provider3,
                category=category,
            )
            a4 = make_recipe(
                'cla_provider.provider_allocation',
                weighted_distribution=1,
                provider=provider4,
                category=category,
            )
            ProviderAllocation.objects.update(modified=as_of-datetime.timedelta(days=1))

            ec = make_recipe('legalaid.eligibility_check_yes', category=category, _quantity=total)

            for n, e in enumerate(ec):
                d = make_recipe('diagnosis.diagnosis_yes',
                                category=category)
                c = make_recipe(
                    'legalaid.eligible_case',
                    id=n+1,
                    eligibility_check=e,
                    diagnosis=d)
                p = helper.get_suggested_provider(category)
                c.assign_to_provider(p)

            self.assertEqual(Case.objects.all().count(), total)

            self.assertWithinAllowedAccuracy(5000, accuracy, provider1.case_set.count())
            self.assertWithinAllowedAccuracy(1000, accuracy, provider2.case_set.count())
            self.assertWithinAllowedAccuracy(1000, accuracy, provider3.case_set.count())
            self.assertWithinAllowedAccuracy(1000, accuracy, provider4.case_set.count())

    def test_get_distribution(self):
        with mock.patch('cla_common.call_centre_availability.current_datetime', datetime.datetime(2015, 7, 7, 11, 59, 0)):
            as_of = timezone.make_aware(
                datetime.datetime(day=7, month=7, year=2015, hour=12, minute=0),
                timezone.get_current_timezone()
            )
            distribution_helper = ProviderDistributionHelper(as_of)

            category = make_recipe('legalaid.category')

            provider1 = make_recipe('cla_provider.provider', active=True)
            provider2 = make_recipe('cla_provider.provider', active=True)
            provider3 = make_recipe('cla_provider.provider', active=True)
            make_recipe(
                'cla_provider.provider_allocation',
                weighted_distribution=1,
                provider=provider1,
                category=category,
            )
            make_recipe(
                'cla_provider.provider_allocation',
                weighted_distribution=1,
                provider=provider2,
                category=category,
            )
            make_recipe(
                'cla_provider.provider_allocation',
                weighted_distribution=1,
                provider=provider3,
                category=category,
            )

            ec = make_recipe('legalaid.eligibility_check_yes', category=category, _quantity=12)

            for i in range(1, 6):
                d = make_recipe('diagnosis.diagnosis_yes',
                                category=category)
                c = make_recipe(
                    'legalaid.eligible_case',
                    id=i,
                    eligibility_check=ec[i],
                    diagnosis=d)
                c.assign_to_provider(provider1)

            for i in range(7, 9):
                d = make_recipe('diagnosis.diagnosis_yes',
                                category=category)
                c = make_recipe(
                    'legalaid.eligible_case',
                    id=i,
                    eligibility_check=ec[i],
                    diagnosis=d)
                c.assign_to_provider(provider2)

            for i in range(9, 10):
                d = make_recipe('diagnosis.diagnosis_yes',
                                category=category)
                c = make_recipe(
                    'legalaid.eligible_case',
                    id=i,
                    eligibility_check=ec[i],
                    diagnosis=d)
                c.assign_to_provider(provider3)

            self.assertDictEqual(
                distribution_helper.get_distribution(category),
                {
                    provider1.pk: 5,
                    provider2.pk: 2,
                    provider3.pk: 1,
                })

    def test_distribution_with_rota(self):
        with mock.patch('cla_common.call_centre_availability.current_datetime', datetime.datetime(2015, 7, 7, 11, 59, 0)):
            as_of = timezone.make_aware(
                datetime.datetime(day=7, month=7, year=2015, hour=12, minute=0),
                timezone.get_current_timezone()
            )
            distribution_helper = ProviderDistributionHelper(as_of)

            category = make_recipe('legalaid.category')

            provider1 = make_recipe('cla_provider.provider', active=True)
            provider2 = make_recipe('cla_provider.provider', active=True)
            aloc1 = make_recipe(
                'cla_provider.provider_allocation',
                weighted_distribution=1,
                provider=provider1,
                category=category,
                modified=as_of,
            )
            aloc1.modified = as_of
            aloc1.save()

            aloc2 = make_recipe(
                'cla_provider.provider_allocation',
                weighted_distribution=1,
                provider=provider2,
                category=category,
                modified=as_of,
            )
            aloc2.modified = as_of
            aloc2.save()

            d = make_recipe('diagnosis.diagnosis_yes',
                            id=1,
                            category=category)

            ec = make_recipe('legalaid.eligibility_check_yes',
                             id=1,
                             category=category)

            c = make_recipe(
                'legalaid.eligible_case',
                id=1,
                eligibility_check=ec,
                diagnosis=d)

            tz = timezone.now().replace(hour=20, minute=59) + datetime.timedelta(days=1)

            with mock.patch('django.utils.timezone.now', lambda: tz):
                c.assign_to_provider(provider1)

            self.assertDictEqual(
                distribution_helper.get_distribution(category),
                {})

            d2 = make_recipe('diagnosis.diagnosis_yes',
                             id=2,
                             category=category)

            ec2 = make_recipe('legalaid.eligibility_check_yes',
                              id=2,
                              category=category)

            c2 = make_recipe(
                'legalaid.eligible_case',
                id=2,
                eligibility_check=ec2,
                diagnosis=d2)

            tz2 = timezone.now().replace(hour=11, minute=59) + datetime.timedelta(days=1)

            with mock.patch('django.utils.timezone.now', lambda: tz2):
                c2.assign_to_provider(provider2)

            self.assertDictEqual(
                distribution_helper.get_distribution(category),
                {
                    provider2.pk: 1,
                })



