from django.test import TestCase
from historic.models import CaseArchived
from freezegun import freeze_time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from cla_butler.constants import delete_option_three_years
from cla_butler.tasks import DeleteOldData


class TestHousekeeping(TestCase):
    def test_cleanup_historic_case_archive(self):
        """ Tests that archived cases that were last modified over 3 years ago will be removed
            whilst ensuring any cases modified less than 3 years ago remain.
        """
        cases_to_be_removed = []
        cases_to_be_kept = []

        with freeze_time(datetime.now() - relativedelta(years=3, days=1)):
            for _ in range(10):
                cases_to_be_removed.append(CaseArchived())
            CaseArchived.objects.bulk_create(cases_to_be_removed)

        with freeze_time(datetime.now() - relativedelta(years=2)):
            for _ in range(15):
                cases_to_be_kept.append(CaseArchived())
            CaseArchived.objects.bulk_create(cases_to_be_kept)

        assert CaseArchived.objects.count() == 25

        # 10 were last modified over 3 years ago and should be deleted
        assert CaseArchived.objects.filter(modified__lte=datetime.now() - relativedelta(years=3)).count() == 10

        DeleteOldData().run(delete_option_three_years)

        # 10 were deleted
        assert CaseArchived.objects.filter(modified__lte=datetime.now() - relativedelta(years=3)).count() == 0

        # And 15 still remain
        assert CaseArchived.objects.count() == 15
