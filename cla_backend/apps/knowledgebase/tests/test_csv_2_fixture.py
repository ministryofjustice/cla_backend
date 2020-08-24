import json
import os
from collections import defaultdict

from django.test import TestCase
from django.core import management

from knowledgebase.management.commands._csv_2_fixture import KnowledgebaseCsvParse


class TestCSV2Fixture(TestCase):
    def load_JSON_fixture_into_DB(self, csv_file_path):
        management.call_command("builddata", "load_knowledgebase_csv", csv_file_path)
        management.call_command(
            "loaddata", os.path.abspath("cla_backend/apps/knowledgebase/fixtures/kb_from_spreadsheet.json")
        )

    def calculate_pk_range(self, article_category_matrices):
        min_range = min(article_category_matrices, key=lambda x: x["pk"])
        max_range = max(article_category_matrices, key=lambda x: x["pk"])
        return min_range["pk"], max_range["pk"]

    def test_fixture_with_required_article_category_fields(self):
        csv_file_path = os.path.abspath("cla_backend/apps/knowledgebase/tests/CSVData/testcsv.csv")
        file = open(csv_file_path)
        csv = KnowledgebaseCsvParse(file)
        outputJSON = csv.fixture_as_json()
        outputList = json.loads(outputJSON)
        expectedList = [
            {u"name": u"Debt"},
            {u"name": u"Education"},
            {u"name": u"Discrimination"},
            {u"name": u"Housing"},
            {u"name": u"Family"},
            {u"name": u"Welfare benefits"},
            {u"name": u"Action against police"},
            {u"name": u"Clinical negligence"},
            {u"name": u"Community care"},
            {u"name": u"Consumer"},
            {u"name": u"Crime"},
            {u"name": u"Employment"},
            {u"name": u"Immigration and asylum"},
            {u"name": u"Mental health"},
            {u"name": u"Miscellaneous"},
            {u"name": u"Personal injury"},
            {u"name": u"Public"},
            {u"name": u"Generic"},
        ]
        self.assertEqual(len(outputList), 18)
        self.assertEqual(outputList[0].keys(), [u"pk", u"model", u"fields"])
        self.assertEqual(outputList[0]["fields"].keys(), [u"created", u"name", u"modified"])

        for output, expectedDict in zip(outputList, expectedList):
            for expectedKey, expectedValue in expectedDict.items():
                self.assertEqual(output["fields"][expectedKey], expectedValue)

        self.load_JSON_fixture_into_DB(csv_file_path)

    def test_fixture_with_valid_entry_type_field(self):
        csv_file_path = os.path.abspath("cla_backend/apps/knowledgebase/tests/CSVData/legal_resource_entry_type.csv")
        file = open(csv_file_path)
        csv = KnowledgebaseCsvParse(file)
        outputJSON = csv.fixture_as_json()
        expectedDict = {
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
        }
        outputList = json.loads(outputJSON)
        output_article_list = filter(lambda x: x["model"] == "knowledgebase.article", outputList)
        self.assertEqual(len(output_article_list), 1)

        article = output_article_list[0]

        self.assertEqual(sorted(article.keys()), [u"fields", u"model", u"pk"])
        self.assertEqual(
            sorted(article["fields"].keys()),
            [
                u"accessibility",
                u"address",
                u"created",
                u"description",
                u"geographic_coverage",
                u"how_to_use",
                u"keywords",
                u"modified",
                u"opening_hours",
                u"organisation",
                u"resource_type",
                u"service_name",
                u"type_of_service",
                u"website",
                u"when_to_use",
            ],
        )

        output_article = output_article_list[0]
        for expectedKey, expectedValue in expectedDict.items():
            self.assertEqual(output_article["fields"][expectedKey], expectedValue)

        self.load_JSON_fixture_into_DB(csv_file_path)

    def test_fixture_handling_with_entry_type_of_legal_resource_for_clients(self):
        csv_file_path = os.path.abspath("cla_backend/apps/knowledgebase/tests/CSVData/legal_resource_entry_type.csv")
        file = open(csv_file_path)
        csv = KnowledgebaseCsvParse(file)
        outputJSON = csv.fixture_as_json()
        outputList = json.loads(outputJSON)
        outputArticle = outputList[-1]
        self.assertEqual(outputArticle["fields"]["resource_type"], u"LEGAL")

    def test_fixture_handling_with_entry_type_of_other_resource_for_clients(self):
        csv_file_path = os.path.abspath("cla_backend/apps/knowledgebase/tests/CSVData/csv_with_entry_type.csv")
        file = open(csv_file_path)
        csv = KnowledgebaseCsvParse(file)
        outputJSON = csv.fixture_as_json()
        outputList = json.loads(outputJSON)
        outputArticle = outputList[-1]
        self.assertEqual(outputArticle["fields"]["resource_type"], u"OTHER")
        self.load_JSON_fixture_into_DB(csv_file_path)

    def test_fixture_with_complete_article(self):
        csv_file_path = os.path.abspath("cla_backend/apps/knowledgebase/tests/CSVData/complete_article.csv")
        file = open(csv_file_path)
        csv = KnowledgebaseCsvParse(file)
        outputJSON = csv.fixture_as_json()
        outputList = json.loads(outputJSON)
        expectedList = [
            {u"article": 1, u"article_category": 1, u"preferred_signpost": False},
            {u"article": 1, u"article_category": 2, u"preferred_signpost": True},
            {u"article": 1, u"article_category": 3, u"preferred_signpost": False},
            {u"article": 1, u"article_category": 4, u"preferred_signpost": False},
            {u"article": 1, u"article_category": 5, u"preferred_signpost": False},
            {u"article": 1, u"article_category": 6, u"preferred_signpost": True},
            {u"article": 1, u"article_category": 7, u"preferred_signpost": False},
            {u"article": 1, u"article_category": 8, u"preferred_signpost": True},
            {u"article": 1, u"article_category": 9, u"preferred_signpost": False},
            {u"article": 1, u"article_category": 10, u"preferred_signpost": True},
            {u"article": 1, u"article_category": 11, u"preferred_signpost": True},
            {u"article": 1, u"article_category": 12, u"preferred_signpost": False},
            {u"article": 1, u"article_category": 13, u"preferred_signpost": True},
            {u"article": 1, u"article_category": 14, u"preferred_signpost": False},
            {u"article": 1, u"article_category": 15, u"preferred_signpost": False},
            {u"article": 1, u"article_category": 16, u"preferred_signpost": False},
            {u"article": 1, u"article_category": 17, u"preferred_signpost": True},
            {u"article": 1, u"article_category": 18, u"preferred_signpost": True},
        ]
        outputList = json.loads(outputJSON)

        output_acm = filter(lambda x: x["model"] == "knowledgebase.articlecategorymatrix", outputList)

        output_acm_record = output_acm[0]

        self.assertEqual(sorted(output_acm_record.keys()), [u"fields", u"model", u"pk"])
        self.assertEqual(
            sorted(output_acm_record["fields"].keys()),
            [u"article", u"article_category", u"created", u"modified", u"preferred_signpost"],
        )

        output_acm_sorted = sorted(output_acm, key=lambda x: x["fields"]["article_category"])
        expected_acm_sorted = sorted(expectedList, key=lambda x: x["article_category"])

        for output, expected in zip(output_acm_sorted, expected_acm_sorted):
            for expectedKey, expectedValue in expected.items():
                self.assertEqual(output["fields"][expectedKey], expectedValue)

        self.assertEqual(len(output_acm), 18)

        min_pk, max_pk = self.calculate_pk_range(output_acm)
        self.assertEqual(min_pk, 1)
        self.assertEqual(max_pk, 18)
        self.load_JSON_fixture_into_DB(csv_file_path)

    def test_fixture_with_multiple_articles(self):
        csv_file_path = os.path.abspath("cla_backend/apps/knowledgebase/tests/CSVData/multiple_articles.csv")
        file = open(csv_file_path)
        csv = KnowledgebaseCsvParse(file)
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
        self.assertEqual(article_1["fields"]["website"], "http://Baz")
        self.assertEqual(article_2["fields"]["website"], "http://Website 2")
        self.assertNotEqual(article_1["pk"], article_2["pk"])

        article_category_matrices = sorted_records["knowledgebase.articlecategorymatrix"]
        min_pk, max_pk = self.calculate_pk_range(article_category_matrices)

        self.assertEqual(len(article_category_matrices), 36)
        self.assertEqual(min_pk, 1)
        self.assertEqual(max_pk, 36)

        first_set_of_acm = filter(lambda x: x["fields"]["article"] == 1, article_category_matrices)
        second_set_of_acm = filter(lambda x: x["fields"]["article"] == 2, article_category_matrices)

        self.assertEqual(len(first_set_of_acm), 18)
        self.assertEqual(len(second_set_of_acm), 18)
        self.load_JSON_fixture_into_DB(csv_file_path)

    def test_fixture_with_empty_csv(self):
        csv_file_path = os.path.abspath("cla_backend/apps/knowledgebase/tests/CSVData/empty_csv.csv")
        file = open(csv_file_path)
        csv = KnowledgebaseCsvParse(file)
        outputJSON = csv.fixture_as_json()
        outputList = json.loads(outputJSON)
        self.assertEqual(len(outputList), 18)
        self.load_JSON_fixture_into_DB(csv_file_path)
