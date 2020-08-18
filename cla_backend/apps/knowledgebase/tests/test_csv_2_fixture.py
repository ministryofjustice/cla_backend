import json
import os
from datetime import datetime
from collections import defaultdict

from django.test import TestCase
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.core import management

from knowledgebase.management.commands._csv_2_fixture import KnowledgebaseCsvParse


class TestCSV2Fixture(TestCase):
    def setUp(self):
        self.datetime_now = datetime.now().replace(tzinfo=timezone.get_current_timezone()).isoformat()

    def find_path_to_csvfile(self, relative_path):
        dirname = os.path.abspath(os.path.dirname(__file__))
        csv_file = "CSVData/{}.csv".format(relative_path)
        return os.path.join(dirname, csv_file)

    def load_JSON_fixture_into_DB(self, relative_path):
        try:
            management.call_command("builddata", "load_knowledgebase_csv", self.find_path_to_csvfile(relative_path))
            management.call_command(
                "loaddata", os.path.abspath("cla_backend/apps/knowledgebase/fixtures/kb_from_spreadsheet.json")
            )
        except Exception as e:
            self.fail(e)
        else:
            print("Record successfully loaded into DB!")

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
        csv_file = self.find_path_to_csvfile("testcsv")
        file = open(csv_file)
        try:
            csv = KnowledgebaseCsvParse(file)
        except SystemExit:
            self.fail("SystemExit Exception with a error code of -1")
        else:
            outputJSON = csv.fixture_as_json()
            outputList = json.loads(outputJSON)
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
            self.compare_length(outputList, expectedList)
            self.compare_list_of_records(outputList, expectedList)
            self.load_JSON_fixture_into_DB("testcsv")

    def test_fixture_with_valid_entry_type_field(self):
        csv_file = self.find_path_to_csvfile("legal_resource_entry_type")
        file = open(csv_file)
        try:
            csv = KnowledgebaseCsvParse(file)
        except SystemExit:
            self.fail("Missing required fields")
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
            self.load_JSON_fixture_into_DB("legal_resource_entry_type")

    def test_fixture_handling_with_entry_type_of_legal_resource_for_clients(self):
        csv_file = self.find_path_to_csvfile("legal_resource_entry_type")
        file = open(csv_file)
        try:
            csv = KnowledgebaseCsvParse(file)
        except SystemExit:
            self.fail("Missing required fields")
        else:
            outputJSON = csv.fixture_as_json()
            outputList = json.loads(outputJSON)
            outputArticle = outputList[-1]
            self.assertEqual(outputArticle["fields"]["resource_type"], u"LEGAL")

    def test_fixture_handling_with_entry_type_of_other_resource_for_clients(self):
        csv_file = self.find_path_to_csvfile("csv_with_entry_type")
        file = open(csv_file)
        try:
            csv = KnowledgebaseCsvParse(file)
        except SystemExit:
            self.fail("Missing required fields")
        else:
            outputJSON = csv.fixture_as_json()
            outputList = json.loads(outputJSON)
            outputArticle = outputList[-1]
            self.assertEqual(outputArticle["fields"]["resource_type"], u"OTHER")

    def test_fixture_with_filled_out_article(self):
        csv_file = self.find_path_to_csvfile("complete_article")
        file = open(csv_file)
        try:
            csv = KnowledgebaseCsvParse(file)
        except SystemExit:
            self.fail("Missing required fields")
        else:
            outputJSON = csv.fixture_as_json()
            outputList = json.loads(outputJSON)
            expectedList = [
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
                        u"preferred_signpost": False,
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
                        u"preferred_signpost": False,
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
                        u"preferred_signpost": True,
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
                        u"preferred_signpost": True,
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
                        u"preferred_signpost": False,
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
                        u"preferred_signpost": False,
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
                        u"preferred_signpost": True,
                    },
                },
            ]
            outputList = json.loads(outputJSON)
            output_acm = filter(lambda x: x["model"] == "knowledgebase.articlecategorymatrix", outputList)
            self.compare_length(output_acm, expectedList)

            pk_range_for_acm = self.calculate_pk_range(expectedList)

            output_sorted_acm, expected_sorted_acm = self.sort_article_category_matrices(output_acm, expectedList)
            self.compare_article_category_matrices(output_sorted_acm, expected_sorted_acm, pk_range_for_acm)

    def test_fixture_with_prefilled_spreadsheet(self):
        csv_file = self.find_path_to_csvfile("pre_filled_spreadsheet")
        file = open(csv_file)
        try:
            csv = KnowledgebaseCsvParse(file)
        except SystemExit:
            self.fail("Missing required fields")
        else:
            outputJSON = csv.fixture_as_json()
            outputList = json.loads(outputJSON)

            sorted_records = defaultdict(list)

            for record in outputList:
                sorted_records[record["model"]].append(record)

            article_category_records = sorted_records["knowledgebase.articlecategory"]
            self.assertEqual(len(article_category_records), 18)

            article_records = sorted_records["knowledgebase.article"]
            article_1, article_2 = article_records

            self.assertEqual(len(article_records), 2)
            self.assertNotEqual(article_1["fields"]["website"], article_2["fields"]["website"])
            self.assertNotEqual(article_1["pk"], article_2["pk"])

            article_category_matrices = sorted_records["knowledgebase.articlecategorymatrix"]
            min_pk, max_pk = self.calculate_pk_range(article_category_matrices)

            self.assertEqual(len(article_category_matrices), 36)
            self.assertEqual(min_pk, 1)
            self.assertEqual(max_pk, 36)

    def test_fixture_with_empty_csv(self):
        csv_file = self.find_path_to_csvfile("empty_csv")
        file = open(csv_file)
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
            ]

            outputList = json.loads(outputJSON)
            self.compare_length(outputList, expectedList)
            self.compare_list_of_records(outputList, expectedList)
            self.load_JSON_fixture_into_DB("empty_csv")
