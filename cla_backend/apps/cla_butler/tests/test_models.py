from django.test import TestCase
from cla_butler.models import DiversityDataCheck, ACTION
from cla_butler.tests.mixins import CreateSampleDiversityData


class DiversityDataCheckModelTestCase(CreateSampleDiversityData, TestCase):
    def test_get_unprocessed_personal_data_qs(self):
        ddc = DiversityDataCheck.objects.create(action=ACTION.CHECK, personal_details_id=self.pd_records_ids[0])
        qs = DiversityDataCheck.get_unprocessed_personal_data_qs(ACTION.CHECK)
        self.assertEqual(qs.count(), 9)
        self.assertNotIn(ddc.pk, qs.values_list("id", flat=True))
