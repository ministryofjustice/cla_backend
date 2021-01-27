from django.test import TestCase
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from freezegun import freeze_time

from cla_butler.tasks import DeleteOldData
from core.tests.mommy_utils import make_recipe
from legalaid.models import Case


class TasksTestCase(TestCase):
    def setUp(self):
        super(TasksTestCase, self).setUp()
        self.delete_old_data = DeleteOldData()

    def create_old_case():
        # Creates a case thats three years old
        freezer = freeze_time(timezone.now() + relativedelta(years=-3))
        freezer.start()
        case = make_recipe("legalaid.case")
        freezer.stop()

        return case

    def test_delete_objects(self):
        make_recipe("legalaid.case")
        cases = Case.objects.all()
        self.delete_old_data._delete_objects(cases)
        cases = Case.objects.all()
        self.assertEqual(len(cases), 0)
