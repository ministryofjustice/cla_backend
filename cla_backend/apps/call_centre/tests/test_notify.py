from django.utils import timezone
from django.test import TestCase
from core.tests.mommy_utils import make_recipe
from cla_provider.tests.test_notify import MockGovNotifyMailBox


class NotifyTestCase(MockGovNotifyMailBox, TestCase):
    def setUp(self):
        super(NotifyTestCase, self).setUp()
        third_party = make_recipe("legalaid.thirdparty_details")
        requires_action_at_10 = timezone.datetime(year=2023, month=5, day=12, hour=10, tzinfo=timezone.utc)
        requires_action_at_11 = timezone.datetime(year=2023, month=5, day=12, hour=11, tzinfo=timezone.utc)
        self.case_third_party = make_recipe(
            "legalaid.case", thirdparty_details=third_party, requires_action_at=requires_action_at_10
        )
        self.case_personal = make_recipe("legalaid.case", requires_action_at=requires_action_at_11)
