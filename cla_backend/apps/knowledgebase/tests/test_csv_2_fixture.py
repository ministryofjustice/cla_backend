from django.test import TestCase
from knowledgebase.management.commands._csv_2_fixture import KnowledgebaseCsvParse


class TestCSV2Fixture(TestCase):
    def test_fixture_with_article_category_fields(self):
        file = open("./KnowledgebaseTestFiles/testcsv.csv")
        csv = KnowledgebaseCsvParse(file)
        json = csv.fixture_as_json()
        print(json, "json")
