from django.test import TestCase
from datetime import datetime
from knowledgebase.management.commands._csv_2_fixture import KnowledgebaseCsvParse
from django.utils import timezone
import json


class TestCSV2Fixture(TestCase):
    def setUp(self):
        self.datetime_now = datetime.now().replace(tzinfo=timezone.get_current_timezone()).isoformat()

    def format_json(self, value):
        return json.dumps(value, indent=4)

    def compare_dicts(self, outputDict, expectedDict):
        for key, value in expectedDict.items():
            self.assertEqual(outputDict[key], value)

    def compare_lists(self, outputList, expectedList):
        for expectedField in expectedList:
            for outputField in outputList:
                if expectedField["pk"] == outputField["pk"]:
                    for key, value in expectedField.items():
                        print(value)
                        if isinstance(value, dict):
                            self.compare_dicts(outputField, expectedField)
                        self.assertEqual(outputField[key], value)

    def test_fixture_with_required_article_category_fields(self):
        file = open("./KnowledgebaseTestFiles/testcsv.csv")
        csv = KnowledgebaseCsvParse(file)
        outputJSON = csv.fixture_as_json()
        expectedList = [
            {
                u"pk": 1,
                u"model": "knowledgebase.articlecategory",
                u"fields": {u"name": u"Debt", u"created": self.datetime_now, u"modified": self.datetime_now},
            },
            {
                u"pk": 2,
                u"model": "knowledgebase.articlecategory",
                u"fields": {u"name": "Education", u"created": self.datetime_now, u"modified": self.datetime_now},
            },
            {
                u"pk": 3,
                u"model": "knowledgebase.articlecategory",
                u"fields": {u"name": "Discrimination", u"created": self.datetime_now, u"modified": self.datetime_now},
            },
            {
                u"pk": 4,
                u"model": "knowledgebase.articlecategory",
                u"fields": {u"name": "Housing", u"created": self.datetime_now, u"modified": self.datetime_now},
            },
            {
                u"pk": 5,
                u"model": "knowledgebase.articlecategory",
                u"fields": {u"name": "Family", u"created": self.datetime_now, u"modified": self.datetime_now},
            },
            {
                u"pk": 6,
                u"model": "knowledgebase.articlecategory",
                u"fields": {
                    u"name": "Welfare benefits",
                    u"created": self.datetime_now,
                    u"modified": self.datetime_now,
                },
            },
            {
                u"pk": 7,
                u"model": "knowledgebase.articlecategory",
                u"fields": {
                    u"name": "Action against police",
                    u"created": self.datetime_now,
                    u"modified": self.datetime_now,
                },
            },
            {
                u"pk": 8,
                u"model": "knowledgebase.articlecategory",
                u"fields": {
                    u"name": "Clinical negligence",
                    u"created": self.datetime_now,
                    u"modified": self.datetime_now,
                },
            },
            {
                u"pk": 9,
                u"model": "knowledgebase.articlecategory",
                u"fields": {u"name": "Community care", u"created": self.datetime_now, u"modified": self.datetime_now},
            },
            {
                u"pk": 10,
                u"model": "knowledgebase.articlecategory",
                u"fields": {u"name": "Consumer", u"created": self.datetime_now, u"modified": self.datetime_now},
            },
            {
                u"pk": 11,
                u"model": "knowledgebase.articlecategory",
                u"fields": {u"name": "Crime", u"created": self.datetime_now, u"modified": self.datetime_now},
            },
            {
                u"pk": 12,
                u"model": "knowledgebase.articlecategory",
                u"fields": {u"name": "Employment", u"created": self.datetime_now, u"modified": self.datetime_now},
            },
            {
                u"pk": 13,
                u"model": "knowledgebase.articlecategory",
                u"fields": {
                    u"name": "Immigration and asylum",
                    u"created": self.datetime_now,
                    u"modified": self.datetime_now,
                },
            },
            {
                u"pk": 14,
                u"model": "knowledgebase.articlecategory",
                u"fields": {u"name": "Mental health", u"created": self.datetime_now, u"modified": self.datetime_now},
            },
            {
                u"pk": 15,
                u"model": "knowledgebase.articlecategory",
                u"fields": {u"name": "Miscelaneous", u"created": self.datetime_now, u"modified": self.datetime_now},
            },
            {
                u"pk": 16,
                u"model": "knowledgebase.articlecategory",
                u"fields": {u"name": "Personal injury", u"created": self.datetime_now, u"modified": self.datetime_now},
            },
            {
                u"pk": 17,
                u"model": "knowledgebase.articlecategory",
                u"fields": {u"name": "Publi", u"created": self.datetime_now, u"modified": self.datetime_now},
            },
            {
                u"pk": 18,
                u"model": "knowledgebase.articlecategory",
                u"fields": {u"name": "Generic", u"created": self.datetime_now, u"modified": self.datetime_now},
            },
        ]
        outputList = json.loads(outputJSON)
        self.compare_lists(outputList, expectedList)


#         expectedJSON = self.format_json(expectedList)
#         self.assertEqual(outputJSON, expectedJSON)
