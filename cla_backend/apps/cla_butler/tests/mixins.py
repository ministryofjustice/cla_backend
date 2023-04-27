from core.tests.mommy_utils import make_recipe
from legalaid.utils import diversity


class CreateSampleDiversityData:
    def setUp(self):
        sample_data = {
            'gender': 'Prefer not to say',
            'religion': 'Prefer not to say',
            'disability': 'PNS - Prefer not to say',
            'ethnicity': 'Prefer not to say',
            'sexual_orientation': 'Prefer Not To Say'
        }
        self.pd_records_ids = [make_recipe("legalaid.personal_details").pk for _ in range(0, 10)]
        for pd_records_id in self.pd_records_ids:
            diversity.save_diversity_data(pd_records_id, sample_data)
