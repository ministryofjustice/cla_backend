import mock

from cla_common.tests.test_bank_holidays_base import TestBankHolidaysBaseTestCase
from cla_common.services import CacheAdapter, TranslationAdapter, translate
from cla_common.call_centre_availability import BankHolidays


class ServicesTestCase(TestBankHolidaysBaseTestCase):
    def test_setting_cache_adpater(self):
        def cache_adapter_factory(**kwargs):
            cache = {}

            def cache_get(name):
                return cache.get(name)

            def cache_set(name, value, *args, **kwargs):
                cache[name] = value

            test_cache = mock.Mock()
            test_cache.get = mock.Mock(side_effect=cache_get)
            test_cache.set = mock.Mock(side_effect=cache_set)
            return test_cache

        CacheAdapter.set_adapter_factory(cache_adapter_factory)
        bank_holidays = BankHolidays()
        bank_holidays._load_dates = mock.Mock()
        bank_holidays._parse_dates = mock.Mock()
        # Get bank holiday days
        bank_holidays.dates
        self.assertTrue(bank_holidays._load_dates.called)

        # Get bank holiday days
        bank_holidays.dates
        self.assertEqual(bank_holidays._load_dates.call_count, 1)

    def test_setting_translation_adpater(self):
        def translation_adapter_factory():
            return lambda string: "--{}--".format(string)

        TranslationAdapter.set_adapter_factory(translation_adapter_factory)
        adapter = TranslationAdapter.get_adapter()
        self.assertEqual(adapter("foo"), "--foo--")

    def test_lazy_translation(self):
        TranslationAdapter.set_adapter_factory(None)
        string = translate("foo")
        # Untranslated
        self.assertEqual(string, "foo")

        def translation_adapter_factory():
            return lambda string_in: "--{}--".format(string_in)

        TranslationAdapter.set_adapter_factory(translation_adapter_factory)
        self.assertEqual(string, "--foo--")
