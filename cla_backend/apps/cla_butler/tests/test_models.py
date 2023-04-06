from django.test import TestCase
from cla_butler.models import DiversityDataCheck, ACTION
from core.tests.mommy_utils import make_recipe
from legalaid.utils import diversity


class DiversityDataCheckModelTestCase(TestCase):
    def test_get_unprocessed_personal_data_qs(self):
        sample_data = {
            'gender': 'Prefer not to say',
            'religion': 'Prefer not to say',
            'disability': 'PNS - Prefer not to say',
            'ethnicity': 'Prefer not to say',
            'sexual_orientation': 'Prefer Not To Say'
        }
        pd_records_ids = [make_recipe("legalaid.personal_details").pk for _ in range(0, 10)]
        for pd_records_id in pd_records_ids:
            diversity.save_diversity_data(pd_records_id, sample_data)

        ddc = DiversityDataCheck.objects.create(action=ACTION.CHECK, personal_details_id=pd_records_ids[0])
        qs = DiversityDataCheck.get_unprocessed_personal_data_qs(ACTION.CHECK)
        self.assertEqual(qs.count(), 9)
        self.assertNotIn(ddc.pk, qs.values_list("id", flat=True))
