import json
from datetime import datetime

from django.test import TestCase
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from knowledgebase.management.commands._csv_2_fixture import KnowledgebaseCsvParse


class TestCSV2Fixture(TestCase):
    def setUp(self):
        self.datetime_now = datetime.now().replace(tzinfo=timezone.get_current_timezone()).isoformat()

    def format_json(self, value):
        return json.dumps(value, indent=4)

    def compare_dicts(self, outputDict, expectedDict):
        for key, value in expectedDict.items():
            parsed_datetime = parse_datetime(value)
            if isinstance(parsed_datetime, datetime):
                self.compare_datetimes(parse_datetime(outputDict[key]), parsed_datetime)
            self.assertIsInstance(value, type(outputDict[key]))

    def compare_datetimes(self, outputDatetime, expectedDatetime):
        time_diff = outputDatetime - expectedDatetime
        time_diff_in_seconds = time_diff.total_seconds()
        self.assertLessEqual(time_diff_in_seconds, 0.5)

    def compare_lists(self, outputList, expectedList):
        for count, expectedObject in enumerate(expectedList):
            outputObject = outputList[count]
            for key, value in expectedObject.items():
                if isinstance(value, dict):
                    self.compare_dicts(outputObject[key], value)
                self.assertIsInstance(value, type(outputObject[key]))

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
        self.compare_lists(outputList, expectedList)
