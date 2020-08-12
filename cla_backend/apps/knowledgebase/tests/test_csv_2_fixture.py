import json
from datetime import datetime

from django.test import TestCase
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from knowledgebase.management.commands._csv_2_fixture import KnowledgebaseCsvParse


class TestCSV2Fixture(TestCase):
    def setUp(self):
        self.datetime_now = datetime.now().replace(tzinfo=timezone.get_current_timezone()).isoformat()

    def calculate_pk_range(self, article_category_matrix):
        min_range = min(article_category_matrix, key=lambda x: x["pk"])
        max_range = max(article_category_matrix, key=lambda x: x["pk"])
        return min_range["pk"], max_range["pk"]

    def sort_article_category_matrices(self, output_category_matrix, expected_category_matrix):
        output_sorted_acm = sorted(output_category_matrix, key=lambda x: x["fields"]["article_category"])
        expected_sorted_acm = sorted(expected_category_matrix, key=lambda x: x["fields"]["article_category"])
        return output_sorted_acm, expected_sorted_acm

    def slice_records(self, output_records, expected_records, start_index=None, end_index=None):
        output_sliced = output_records[start_index:end_index]
        expected_sliced = expected_records[start_index:end_index]
        return output_sliced, expected_sliced

    def compare_dicts(self, outputDict, expectedDict):
        for key, outputValue in outputDict.items():
            expectedValue = expectedDict[key]
            self.assertEqual(type(outputValue), type(expectedValue))
            if isinstance(outputValue, unicode) and isinstance(parse_datetime(outputValue), datetime):
                self.compare_datetimes(parse_datetime(outputValue), parse_datetime(expectedValue))
            else:
                self.assertEqual(outputValue, expectedValue)

    def compare_datetimes(self, outputDatetime, expectedDatetime):
        time_diff = outputDatetime - expectedDatetime
        time_diff_in_seconds = time_diff.total_seconds()
        self.assertLessEqual(time_diff_in_seconds, 0.5)

    def compare_list_of_records(self, outputList, expectedList):
        for outputObject, expectedObject in zip(outputList, expectedList):
            self.compare_length(outputObject, expectedObject)
            for key, outputValue in outputObject.items():
                expectedValue = expectedObject[key]
                self.assertEqual(type(outputValue), type(expectedValue))
                if isinstance(outputValue, dict):
                    self.compare_dicts(outputValue, expectedValue)
                else:
                    self.assertEqual(outputValue, expectedValue)

    def compare_length(self, output, expected):
        self.assertEqual(len(output), len(expected))

    def compare_article_category_matrices(self, output, expected, pk_range):
        for outputObj, expectedObj in zip(output, expected):
            self.compare_length(outputObj, expectedObj)
            for key, outputValue in outputObj.items():
                expectedValue = expectedObj[key]
                if key == "pk":
                    self.assertEqual(type(outputValue), type(expectedValue))
                    min_pk_value, max_pk_value = pk_range
                    self.assertGreaterEqual(outputValue, min_pk_value)
                    self.assertLessEqual(outputValue, max_pk_value)
                elif isinstance(outputValue, dict):
                    self.compare_dicts(outputValue, expectedValue)
                else:
                    self.assertEqual(type(outputValue), type(expectedValue))
                    self.assertEqual(outputValue, expectedValue)

    def test_fixture_with_required_article_category_fields(self):
        file = open("./cla_backend/apps/knowledgebase/tests/CSVData/testcsv.csv")
        csv = KnowledgebaseCsvParse(file)
        outputJSON = csv.fixture_as_json()
        expectedList = [
            {
                u"pk": 1,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Debt",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 2,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Education",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 3,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Discrimination",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 4,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Housing",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 5,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Family",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 6,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Welfare benefits",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 7,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Action against police",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 8,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Clinical negligence",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 9,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Community care",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 10,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Consumer",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 11,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Crime",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 12,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Employment",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 13,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Immigration and asylum",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 14,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Mental health",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 15,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Miscellaneous",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 16,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Personal injury",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 17,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Public",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 18,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Generic",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
        ]
        outputList = json.loads(outputJSON)
        self.compare_length(outputList, expectedList)
        self.compare_list_of_records(outputList, expectedList)

    def test_fixture_with_other_resource_for_clients_entry_type(self):
        file = open("./cla_backend/apps/knowledgebase/tests/CSVData/csv_with_entry_type.csv")
        csv = KnowledgebaseCsvParse(file)
        outputJSON = csv.fixture_as_json()
        expectedList = [
            {
                u"pk": 1,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Debt",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 2,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Education",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 3,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Discrimination",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 4,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Housing",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 5,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Family",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 6,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Welfare benefits",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 7,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Action against police",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 8,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Clinical negligence",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 9,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Community care",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 10,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Consumer",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 11,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Crime",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 12,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Employment",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 13,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Immigration and asylum",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 14,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Mental health",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 15,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Miscellaneous",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 16,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Personal injury",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 17,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Public",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 18,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Generic",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 1,
                "model": u"knowledgebase.article",
                "fields": {
                    "created": u"{date}".format(date=self.datetime_now),
                    "modified": u"{date}".format(date=self.datetime_now),
                    "resource_type": u"OTHER",
                    "website": u"http://Baz",
                    "geographic_coverage": u"Baz",
                    "type_of_service": u"Baz",
                    "description": u"Bar",
                    "service_name": u"Bar",
                    "organisation": u"Foo",
                    "accessibility": u"Foo",
                    "when_to_use": u"Baz",
                    "how_to_use": u"Foo",
                    "address": u"Foo",
                    "keywords": u"Bar",
                    "opening_hours": u"Bar",
                },
            },
        ]
        outputList = json.loads(outputJSON)
        self.compare_length(outputList, expectedList)
        self.compare_list_of_records(outputList, expectedList)

    def test_fixture_with_legal_resource_for_clients_entry_type(self):
        file = open("./cla_backend/apps/knowledgebase/tests/CSVData/legal_resource_entry_type.csv")
        csv = KnowledgebaseCsvParse(file)
        outputJSON = csv.fixture_as_json()
        expectedList = [
            {
                u"pk": 1,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Debt",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 2,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Education",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 3,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Discrimination",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 4,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Housing",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 5,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Family",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 6,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Welfare benefits",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 7,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Action against police",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 8,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Clinical negligence",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 9,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Community care",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 10,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Consumer",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 11,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Crime",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 12,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Employment",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 13,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Immigration and asylum",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 14,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Mental health",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 15,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Miscellaneous",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 16,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Personal injury",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 17,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Public",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 18,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Generic",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 1,
                "model": u"knowledgebase.article",
                "fields": {
                    "created": u"{date}".format(date=self.datetime_now),
                    "modified": u"{date}".format(date=self.datetime_now),
                    "resource_type": u"LEGAL",
                    "website": u"https://www.google.com",
                    "geographic_coverage": u"Baz",
                    "type_of_service": u"Baz",
                    "description": u"Bar",
                    "service_name": u"Bar",
                    "organisation": u"Foo",
                    "accessibility": u"Foo",
                    "when_to_use": u"Baz",
                    "how_to_use": u"Foo",
                    "address": u"Foo",
                    "keywords": u"Bar",
                    "opening_hours": u"Bar",
                },
            },
        ]
        outputList = json.loads(outputJSON)
        self.compare_length(outputList, expectedList)
        self.compare_list_of_records(outputList, expectedList)

    def test_fixture_with_prefilled_spreadsheet(self):
        file = open("./cla_backend/apps/knowledgebase/tests/CSVData/pre_filled_spreadsheet.csv")
        csv = KnowledgebaseCsvParse(file)
        outputJSON = csv.fixture_as_json()
        expectedList = [
            {
                u"pk": 1,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Debt",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 2,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Education",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 3,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Discrimination",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 4,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Housing",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 5,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Family",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 6,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Welfare benefits",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 7,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Action against police",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 8,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Clinical negligence",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 9,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Community care",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 10,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Consumer",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 11,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Crime",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 12,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Employment",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 13,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Immigration and asylum",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 14,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Mental health",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 15,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Miscellaneous",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 16,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Personal injury",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 17,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Public",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 18,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Generic",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 1,
                "model": u"knowledgebase.article",
                "fields": {
                    "created": u"{date}".format(date=self.datetime_now),
                    "modified": u"{date}".format(date=self.datetime_now),
                    "resource_type": u"LEGAL",
                    "website": u"http://Baz",
                    "geographic_coverage": u"Baz",
                    "type_of_service": u"Baz",
                    "description": u"Bar",
                    "service_name": u"Bar",
                    "organisation": u"Foo",
                    "accessibility": u"Foo",
                    "when_to_use": u"Baz",
                    "how_to_use": u"Foo",
                    "address": u"Foo",
                    "keywords": u"Bar",
                    "opening_hours": u"Bar",
                },
            },
            {
                u"pk": 1,
                u"model": u"knowledgebase.articlecategorymatrix",
                u"fields": {
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                    u"article": 1,
                    u"article_category": 1,
                    u"preferred_signpost": False,
                },
            },
            {
                u"pk": 2,
                u"model": u"knowledgebase.articlecategorymatrix",
                u"fields": {
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                    u"article": 1,
                    u"article_category": 2,
                    u"preferred_signpost": True,
                },
            },
            {
                u"pk": 3,
                u"model": u"knowledgebase.articlecategorymatrix",
                u"fields": {
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                    u"article": 1,
                    u"article_category": 3,
                    u"preferred_signpost": False,
                },
            },
            {
                u"pk": 4,
                u"model": u"knowledgebase.articlecategorymatrix",
                u"fields": {
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                    u"article": 1,
                    u"article_category": 4,
                    u"preferred_signpost": True,
                },
            },
            {
                u"pk": 5,
                u"model": u"knowledgebase.articlecategorymatrix",
                u"fields": {
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                    u"article": 1,
                    u"article_category": 5,
                    u"preferred_signpost": False,
                },
            },
            {
                u"pk": 6,
                u"model": u"knowledgebase.articlecategorymatrix",
                u"fields": {
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                    u"article": 1,
                    u"article_category": 6,
                    u"preferred_signpost": True,
                },
            },
            {
                u"pk": 7,
                u"model": u"knowledgebase.articlecategorymatrix",
                u"fields": {
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                    u"article": 1,
                    u"article_category": 7,
                    u"preferred_signpost": True,
                },
            },
            {
                u"pk": 8,
                u"model": u"knowledgebase.articlecategorymatrix",
                u"fields": {
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                    u"article": 1,
                    u"article_category": 8,
                    u"preferred_signpost": True,
                },
            },
            {
                u"pk": 9,
                u"model": u"knowledgebase.articlecategorymatrix",
                u"fields": {
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                    u"article": 1,
                    u"article_category": 9,
                    u"preferred_signpost": False,
                },
            },
            {
                u"pk": 10,
                u"model": u"knowledgebase.articlecategorymatrix",
                u"fields": {
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                    u"article": 1,
                    u"article_category": 10,
                    u"preferred_signpost": False,
                },
            },
            {
                u"pk": 11,
                u"model": u"knowledgebase.articlecategorymatrix",
                u"fields": {
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                    u"article": 1,
                    u"article_category": 11,
                    u"preferred_signpost": False,
                },
            },
            {
                u"pk": 12,
                u"model": u"knowledgebase.articlecategorymatrix",
                u"fields": {
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                    u"article": 1,
                    u"article_category": 12,
                    u"preferred_signpost": False,
                },
            },
            {
                u"pk": 13,
                u"model": u"knowledgebase.articlecategorymatrix",
                u"fields": {
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                    u"article": 1,
                    u"article_category": 13,
                    u"preferred_signpost": True,
                },
            },
            {
                u"pk": 14,
                u"model": u"knowledgebase.articlecategorymatrix",
                u"fields": {
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                    u"article": 1,
                    u"article_category": 14,
                    u"preferred_signpost": True,
                },
            },
            {
                u"pk": 15,
                u"model": u"knowledgebase.articlecategorymatrix",
                u"fields": {
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                    u"article": 1,
                    u"article_category": 15,
                    u"preferred_signpost": False,
                },
            },
            {
                u"pk": 16,
                u"model": u"knowledgebase.articlecategorymatrix",
                u"fields": {
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                    u"article": 1,
                    u"article_category": 16,
                    u"preferred_signpost": True,
                },
            },
            {
                u"pk": 17,
                u"model": u"knowledgebase.articlecategorymatrix",
                u"fields": {
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                    u"article": 1,
                    u"article_category": 17,
                    u"preferred_signpost": True,
                },
            },
            {
                u"pk": 18,
                u"model": u"knowledgebase.articlecategorymatrix",
                u"fields": {
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                    u"article": 1,
                    u"article_category": 18,
                    u"preferred_signpost": False,
                },
            },
            {
                u"pk": 2,
                "model": u"knowledgebase.article",
                "fields": {
                    "created": u"{date}".format(date=self.datetime_now),
                    "modified": u"{date}".format(date=self.datetime_now),
                    "resource_type": u"OTHER",
                    "website": u"http://Website 2",
                    "geographic_coverage": u"Coverage 2",
                    "type_of_service": u"Type of service 2",
                    "description": u"Description 2",
                    "service_name": u"Service 2",
                    "organisation": u"Organisation 2",
                    "accessibility": u"Accessibility 2",
                    "when_to_use": u"When to use 2",
                    "how_to_use": u"Guidance 2",
                    "address": u"Address 2",
                    "keywords": u"Current keywords 2",
                    "opening_hours": u"Opening hours 2",
                },
            },
            {
                u"pk": 19,
                u"model": u"knowledgebase.articlecategorymatrix",
                u"fields": {
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                    u"article": 2,
                    u"article_category": 1,
                    u"preferred_signpost": False,
                },
            },
            {
                u"pk": 20,
                u"model": u"knowledgebase.articlecategorymatrix",
                u"fields": {
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                    u"article": 2,
                    u"article_category": 2,
                    u"preferred_signpost": False,
                },
            },
            {
                u"pk": 21,
                u"model": u"knowledgebase.articlecategorymatrix",
                u"fields": {
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                    u"article": 2,
                    u"article_category": 3,
                    u"preferred_signpost": False,
                },
            },
            {
                u"pk": 22,
                u"model": u"knowledgebase.articlecategorymatrix",
                u"fields": {
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                    u"article": 2,
                    u"article_category": 4,
                    u"preferred_signpost": False,
                },
            },
            {
                u"pk": 23,
                u"model": u"knowledgebase.articlecategorymatrix",
                u"fields": {
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                    u"article": 2,
                    u"article_category": 5,
                    u"preferred_signpost": False,
                },
            },
            {
                u"pk": 24,
                u"model": u"knowledgebase.articlecategorymatrix",
                u"fields": {
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                    u"article": 2,
                    u"article_category": 6,
                    u"preferred_signpost": True,
                },
            },
            {
                u"pk": 25,
                u"model": u"knowledgebase.articlecategorymatrix",
                u"fields": {
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                    u"article": 2,
                    u"article_category": 7,
                    u"preferred_signpost": True,
                },
            },
            {
                u"pk": 26,
                u"model": u"knowledgebase.articlecategorymatrix",
                u"fields": {
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                    u"article": 2,
                    u"article_category": 8,
                    u"preferred_signpost": True,
                },
            },
            {
                u"pk": 27,
                u"model": u"knowledgebase.articlecategorymatrix",
                u"fields": {
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                    u"article": 2,
                    u"article_category": 9,
                    u"preferred_signpost": True,
                },
            },
            {
                u"pk": 28,
                u"model": u"knowledgebase.articlecategorymatrix",
                u"fields": {
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                    u"article": 2,
                    u"article_category": 10,
                    u"preferred_signpost": True,
                },
            },
            {
                u"pk": 29,
                u"model": u"knowledgebase.articlecategorymatrix",
                u"fields": {
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                    u"article": 2,
                    u"article_category": 11,
                    u"preferred_signpost": True,
                },
            },
            {
                u"pk": 30,
                u"model": u"knowledgebase.articlecategorymatrix",
                u"fields": {
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                    u"article": 2,
                    u"article_category": 12,
                    u"preferred_signpost": True,
                },
            },
            {
                u"pk": 31,
                u"model": u"knowledgebase.articlecategorymatrix",
                u"fields": {
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                    u"article": 2,
                    u"article_category": 13,
                    u"preferred_signpost": True,
                },
            },
            {
                u"pk": 32,
                u"model": u"knowledgebase.articlecategorymatrix",
                u"fields": {
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                    u"article": 2,
                    u"article_category": 14,
                    u"preferred_signpost": False,
                },
            },
            {
                u"pk": 33,
                u"model": u"knowledgebase.articlecategorymatrix",
                u"fields": {
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                    u"article": 2,
                    u"article_category": 15,
                    u"preferred_signpost": False,
                },
            },
            {
                u"pk": 34,
                u"model": u"knowledgebase.articlecategorymatrix",
                u"fields": {
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                    u"article": 2,
                    u"article_category": 16,
                    u"preferred_signpost": False,
                },
            },
            {
                u"pk": 35,
                u"model": u"knowledgebase.articlecategorymatrix",
                u"fields": {
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                    u"article": 2,
                    u"article_category": 17,
                    u"preferred_signpost": True,
                },
            },
            {
                u"pk": 36,
                u"model": u"knowledgebase.articlecategorymatrix",
                u"fields": {
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                    u"article": 2,
                    u"article_category": 18,
                    u"preferred_signpost": True,
                },
            },
        ]
        outputList = json.loads(outputJSON)

        self.compare_length(outputList, expectedList)

        # Refactor
        output_article_categories, expected_article_categories = self.slice_records(
            outputList, expectedList, end_index=18
        )
        self.compare_list_of_records(output_article_categories, expected_article_categories)

        output_article_1, expected_article_1 = self.slice_records(outputList, expectedList, 18, 19)
        self.compare_list_of_records(output_article_1, expected_article_1)

        output_acm_1, expected_acm_1 = self.slice_records(outputList, expectedList, 19, 37)
        pk_range_acm_1 = self.calculate_pk_range(expected_acm_1)
        output_sorted_acm_1, expected_sorted_acm_1 = self.sort_article_category_matrices(output_acm_1, expected_acm_1)
        self.compare_article_category_matrices(output_sorted_acm_1, expected_sorted_acm_1, pk_range_acm_1)

        output_article_2, expected_article_2 = self.slice_records(outputList, expectedList, 37, 38)
        self.compare_list_of_records(output_article_2, expected_article_2)

        # Remove these two lines. Same as output_acm2, expected_acm_2
        output_article_2_category_matrix = outputList[-18:]
        expected_article_2_category_matrix = expectedList[-18:]

        output_acm_2, expected_acm_2 = self.slice_records(outputList, expectedList, -18)
        pk_range_acm_2 = self.calculate_pk_range(expected_article_2_category_matrix)
        output_sorted_acm_2, expected_sorted_acm_2 = self.sort_article_category_matrices(
            output_article_2_category_matrix, expected_article_2_category_matrix
        )
        self.compare_article_category_matrices(output_sorted_acm_2, expected_sorted_acm_2, pk_range_acm_2)

    def test_fixture_with_empty_csv(self):
        file = open("./cla_backend/apps/knowledgebase/tests/CSVData/empty_csv.csv")
        csv = KnowledgebaseCsvParse(file)
        outputJSON = csv.fixture_as_json()
        expectedList = [
            {
                u"pk": 1,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Debt",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 2,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Education",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 3,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Discrimination",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 4,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Housing",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 5,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Family",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 6,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Welfare benefits",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 7,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Action against police",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 8,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Clinical negligence",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 9,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Community care",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 10,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Consumer",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 11,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Crime",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 12,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Employment",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 13,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Immigration and asylum",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 14,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Mental health",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 15,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Miscellaneous",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 16,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Personal injury",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 17,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Public",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
            {
                u"pk": 18,
                u"model": u"knowledgebase.articlecategory",
                u"fields": {
                    u"name": u"Generic",
                    u"created": u"{date}".format(date=self.datetime_now),
                    u"modified": u"{date}".format(date=self.datetime_now),
                },
            },
        ]

        outputList = json.loads(outputJSON)
        self.compare_length(outputList, expectedList)
        self.compare_list_of_records(outputList, expectedList)

    def test_fixture_with_helpline_field_removed(self):
        file = open("./cla_backend/apps/knowledgebase/tests/CSVData/csv_with_no_helpline_field.csv")
        try:
            csv = KnowledgebaseCsvParse(file)
        except SystemExit:
            self.fail("SystemExit Exception with a error code of -1")
        else:
            outputJSON = csv.fixture_as_json()
            expectedList = [
                {
                    u"pk": 1,
                    u"model": u"knowledgebase.articlecategory",
                    u"fields": {
                        u"name": u"Debt",
                        u"created": u"{date}".format(date=self.datetime_now),
                        u"modified": u"{date}".format(date=self.datetime_now),
                    },
                },
                {
                    u"pk": 2,
                    u"model": u"knowledgebase.articlecategory",
                    u"fields": {
                        u"name": u"Education",
                        u"created": u"{date}".format(date=self.datetime_now),
                        u"modified": u"{date}".format(date=self.datetime_now),
                    },
                },
                {
                    u"pk": 3,
                    u"model": u"knowledgebase.articlecategory",
                    u"fields": {
                        u"name": u"Discrimination",
                        u"created": u"{date}".format(date=self.datetime_now),
                        u"modified": u"{date}".format(date=self.datetime_now),
                    },
                },
                {
                    u"pk": 4,
                    u"model": u"knowledgebase.articlecategory",
                    u"fields": {
                        u"name": u"Housing",
                        u"created": u"{date}".format(date=self.datetime_now),
                        u"modified": u"{date}".format(date=self.datetime_now),
                    },
                },
                {
                    u"pk": 5,
                    u"model": u"knowledgebase.articlecategory",
                    u"fields": {
                        u"name": u"Family",
                        u"created": u"{date}".format(date=self.datetime_now),
                        u"modified": u"{date}".format(date=self.datetime_now),
                    },
                },
                {
                    u"pk": 6,
                    u"model": u"knowledgebase.articlecategory",
                    u"fields": {
                        u"name": u"Welfare benefits",
                        u"created": u"{date}".format(date=self.datetime_now),
                        u"modified": u"{date}".format(date=self.datetime_now),
                    },
                },
                {
                    u"pk": 7,
                    u"model": u"knowledgebase.articlecategory",
                    u"fields": {
                        u"name": u"Action against police",
                        u"created": u"{date}".format(date=self.datetime_now),
                        u"modified": u"{date}".format(date=self.datetime_now),
                    },
                },
                {
                    u"pk": 8,
                    u"model": u"knowledgebase.articlecategory",
                    u"fields": {
                        u"name": u"Clinical negligence",
                        u"created": u"{date}".format(date=self.datetime_now),
                        u"modified": u"{date}".format(date=self.datetime_now),
                    },
                },
                {
                    u"pk": 9,
                    u"model": u"knowledgebase.articlecategory",
                    u"fields": {
                        u"name": u"Community care",
                        u"created": u"{date}".format(date=self.datetime_now),
                        u"modified": u"{date}".format(date=self.datetime_now),
                    },
                },
                {
                    u"pk": 10,
                    u"model": u"knowledgebase.articlecategory",
                    u"fields": {
                        u"name": u"Consumer",
                        u"created": u"{date}".format(date=self.datetime_now),
                        u"modified": u"{date}".format(date=self.datetime_now),
                    },
                },
                {
                    u"pk": 11,
                    u"model": u"knowledgebase.articlecategory",
                    u"fields": {
                        u"name": u"Crime",
                        u"created": u"{date}".format(date=self.datetime_now),
                        u"modified": u"{date}".format(date=self.datetime_now),
                    },
                },
                {
                    u"pk": 12,
                    u"model": u"knowledgebase.articlecategory",
                    u"fields": {
                        u"name": u"Employment",
                        u"created": u"{date}".format(date=self.datetime_now),
                        u"modified": u"{date}".format(date=self.datetime_now),
                    },
                },
                {
                    u"pk": 13,
                    u"model": u"knowledgebase.articlecategory",
                    u"fields": {
                        u"name": u"Immigration and asylum",
                        u"created": u"{date}".format(date=self.datetime_now),
                        u"modified": u"{date}".format(date=self.datetime_now),
                    },
                },
                {
                    u"pk": 14,
                    u"model": u"knowledgebase.articlecategory",
                    u"fields": {
                        u"name": u"Mental health",
                        u"created": u"{date}".format(date=self.datetime_now),
                        u"modified": u"{date}".format(date=self.datetime_now),
                    },
                },
                {
                    u"pk": 15,
                    u"model": u"knowledgebase.articlecategory",
                    u"fields": {
                        u"name": u"Miscellaneous",
                        u"created": u"{date}".format(date=self.datetime_now),
                        u"modified": u"{date}".format(date=self.datetime_now),
                    },
                },
                {
                    u"pk": 16,
                    u"model": u"knowledgebase.articlecategory",
                    u"fields": {
                        u"name": u"Personal injury",
                        u"created": u"{date}".format(date=self.datetime_now),
                        u"modified": u"{date}".format(date=self.datetime_now),
                    },
                },
                {
                    u"pk": 17,
                    u"model": u"knowledgebase.articlecategory",
                    u"fields": {
                        u"name": u"Public",
                        u"created": u"{date}".format(date=self.datetime_now),
                        u"modified": u"{date}".format(date=self.datetime_now),
                    },
                },
                {
                    u"pk": 18,
                    u"model": u"knowledgebase.articlecategory",
                    u"fields": {
                        u"name": u"Generic",
                        u"created": u"{date}".format(date=self.datetime_now),
                        u"modified": u"{date}".format(date=self.datetime_now),
                    },
                },
                {
                    u"pk": 1,
                    "model": u"knowledgebase.article",
                    "fields": {
                        "created": u"{date}".format(date=self.datetime_now),
                        "modified": u"{date}".format(date=self.datetime_now),
                        "resource_type": u"OTHER",
                        "website": u"http://Website 2",
                        "geographic_coverage": u"Coverage 2",
                        "type_of_service": u"Type of service 2",
                        "description": u"Description",
                        "service_name": u"Service",
                        "organisation": u"Organisation",
                        "accessibility": u"Accessibility 2",
                        "when_to_use": u"When to use",
                        "how_to_use": u"Guidance 2",
                        "address": u"Address 2",
                        "keywords": u"Current keywords 2",
                        "opening_hours": u"Opening hours 2",
                    },
                },
            ]
            outputList = json.loads(outputJSON)
            self.compare_length(outputList, expectedList)
            self.compare_list_of_records(outputList, expectedList)


#         outputList = json.loads(outputJSON)
#         self.compare_length(outputList, expectedList)
#         self.compare_list_of_records(outputList, expectedList)
#         self.assertEqual(output, expected)
