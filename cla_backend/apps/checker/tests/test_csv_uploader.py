from unittest import TestCase
from ..utils import CallbackTimeSlotCSVImporter
from django.core.exceptions import ValidationError


class TestValidateRow(TestCase):
    def setUp(self):
        self.csv_importer = CallbackTimeSlotCSVImporter()

    def test_valid_row(self):
        valid_csv_rows = [['12/05/2024', '1330', '5'],
                          ['31/03/2024', '0900', '999999'],
                          ['12/5/1999', '1330', '5'],
                          ['12/06/2024', '1000', '0'],
                          ['12/05/2040', '1330', '1234'],
                          ['1/1/2015', '1330', '5']]
        for row in valid_csv_rows:
            # If an exception is raised this test will fail.
            self.csv_importer.validate_row(row)

    def test_malformed_date(self):
        malformed_csv_dates = [['-12/05/2024', '1330', '5'],
                               ['31/2/2025', '1330', '5'],
                               ['29/2/2025', '1330', '5'],
                               ['29-2-2025', '1330', '5'],
                               ['2922025', '1330', '5'],
                               ['2024-5-1', '0900', '6'],
                               ['abcd', '0900', '6'],
                               ['', '0900', '6'],
                               [',', '0900', '6']]
        for row in malformed_csv_dates:
            self.assertRaisesRegexp(ValidationError, "Write the date in this format: dd/mm/yyyy", self.csv_importer.validate_row, row)

    def test_malformed_time(self):
        malformed_csv_times = [['12/06/2024', '-1330', '5'],
                               ['31/05/2024', 'abcd', '999999'],
                               ['12/5/2002', '0901', '5'],
                               ['13/06/2024', '900', '0'],
                               ['12/05/2040', '9', '1234'],
                               ['1/1/2015', '', '5'],
                               ['1/2/2015', ',', '5']]
        for row in malformed_csv_times:
            self.assertRaisesRegexp(ValidationError, "Check the time is correct, for example, 1500", self.csv_importer.validate_row, row)

    def test_malformed_capacity(self):
        malformed_csv_capacity = [['12/08/2024', '1330', ''],
                                  ['31/03/2024', '0900', '1.1'],
                                  ['12/5/1999', '1330', 'a']]
        for row in malformed_csv_capacity:
            self.assertRaisesRegexp(ValidationError, "Write capacity as a number, for example: 1, 2, 10", self.csv_importer.validate_row, row)

        negative_csv_capacity = ['01/01/2000', '0900', '-5']
        self.assertRaisesRegexp(ValidationError, "The capacity must be 0 or more", self.csv_importer.validate_row, negative_csv_capacity)
