import datetime
import copy
from django.test import TestCase
from knowledgebase.models import Article, TelephoneNumber, ArticleCategoryMatrix
from knowledgebase.utils.csv_user_import import KnowledgebaseCSVImporter
from knowledgebase.utils.csv_user_import_mappings import (
    ARTICLE_COLUMN_FIELD_MAPPING,
    TELEPHONE_COLUMN_FIELD_MAPPING,
    ARTICLE_CATEGORY_MATRIX_COLUMN_FIELD_MAPPING,
)
from core.tests.mommy_utils import make_recipe


class KnowledgebaseCSVImporterTester(TestCase):
    _CSV_ROW = [
        "NEW",
        "2014-06-27 14:52:55.547000+00:00",
        "2015-01-28 15:06:18.718000+00:00",
        "LEGAL",
        "LAA",
        "[PREF DISCRIMINATION]",
        "LAA (Legal Aid Agency)",
        "https,//www.gov.uk/government/organisations/legal-aid-agency",
        "",
        "This is the article description",
        "This is the article description",
        "This is how to use it",
        "This is when to use it",
        """102 Petty France
        LONDON
        SW1H 9AJ
        """,
        """Monday-Friday, 8am-8pm
        Saturday, 9am-1pm
        """,
        "employment, helpline, employers, contract, tribunal, grievance",
        "UK",
        "Employment advice helpline",
        "This is accessible text",
        "",
        "0300 123 1100",
        "Text relay",
        "18001 0300 123 1100",
        "",
        "",
        "",
        "",
        "Employment",
        "FALSE",
        "Discrimination",
        "TRUE",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
    ]

    def setUp(self):
        self.importer = KnowledgebaseCSVImporter()
        self.row = copy.copy(self._CSV_ROW)

    def test_article_row_import__new_article(self):
        article = self.importer.get_article_from_row(self.row)
        # We expect the pk value of the new article to be None
        expected = self.row
        expected[0] = None
        self._assert_row_against_article(expected, article)

    def test_article_row_import__existing_article(self):
        existing_article = make_recipe("knowledgebase.article")
        # Set the pk field in the csv row to to an existing Article pk
        expected = self.row
        expected[0] = existing_article.pk
        article = self.importer.get_article_from_row(self.row)
        self._assert_row_against_article(expected, article)

    def test_article_row_import__missing_pk(self):
        # Set the pk field in the csv row to to a value that does not exist
        self.row[0] = 1000
        with self.assertRaisesMessage(ValueError, "Could not find article with an ID of : 1000"):
            self.importer.get_article_from_row(self.row)

    def test_telephone_numbers_row(self):
        article = make_recipe("knowledgebase.article")
        telephone_numbers = self.importer.get_telephone_numbers_from_row(article, self.row)
        self.assertEqual(len(telephone_numbers), 2)
        self._assert_row_telephone(self.row, TELEPHONE_COLUMN_FIELD_MAPPING[0], telephone_numbers[0])
        self._assert_row_telephone(self.row, TELEPHONE_COLUMN_FIELD_MAPPING[1], telephone_numbers[1])

    def test_article_category_matrices_from_row(self):
        employment_category = make_recipe("knowledgebase.article_category", name="Employment")
        discrimination_category = make_recipe("knowledgebase.article_category", name="Discrimination")
        article = make_recipe("knowledgebase.article")
        matrices = self.importer.get_article_category_matrices_from_row(article, self.row)
        self.assertEqual(len(matrices), 2)
        self.assertEqual(matrices[0].article_category, employment_category)
        self.assertFalse(matrices[0].preferred_signpost)
        self.assertEqual(matrices[1].article_category, discrimination_category)
        self.assertTrue(matrices[1].preferred_signpost)

    def test_article_category_matrices_from_row__non_existing_category(self):
        article = make_recipe("knowledgebase.article")
        with self.assertRaisesMessage(ValueError, "Could not find category with name: Employment"):
            self.importer.get_article_category_matrices_from_row(article, self.row)

    def test_article_category_matrices_from_row__invalid_preferred_signpost(self):
        make_recipe("knowledgebase.article_category", name="Employment")
        article = make_recipe("knowledgebase.article")
        with self.assertRaisesMessage(ValueError, "Yes is an invalid value for Preferred signpost"):
            signpost_index = ARTICLE_CATEGORY_MATRIX_COLUMN_FIELD_MAPPING[0][1][0]
            self.row[signpost_index] = "Yes"
            self.importer.get_article_category_matrices_from_row(article, self.row)

    def test_save(self):
        self.assertEqual(Article.objects.count(), 0)
        self.assertEqual(TelephoneNumber.objects.count(), 0)
        self.assertEqual(ArticleCategoryMatrix.objects.count(), 0)

        make_recipe("knowledgebase.article_category", name="Employment")
        make_recipe("knowledgebase.article_category", name="Discrimination")

        article = self.importer.get_article_from_row(self.row)
        telephone_numbers = self.importer.get_telephone_numbers_from_row(article, self.row)
        article_category_matrices = self.importer.get_article_category_matrices_from_row(article, self.row)
        rows = [
            {
                "article": article,
                "telephone_numbers": telephone_numbers,
                "article_category_matrices": article_category_matrices,
            }
        ]

        self.importer.save(rows)

        self.assertEqual(Article.objects.count(), 1)
        self.assertEqual(article.article_category.count(), 2)
        self.assertEqual(TelephoneNumber.objects.filter(article=article).count(), 2)

    def test_save_transaction(self):
        self.assertEqual(Article.objects.count(), 0)
        self.assertEqual(TelephoneNumber.objects.count(), 0)
        self.assertEqual(ArticleCategoryMatrix.objects.count(), 0)

        make_recipe("knowledgebase.article_category", name="Employment")
        make_recipe("knowledgebase.article_category", name="Discrimination")

        article = self.importer.get_article_from_row(self.row)
        telephone_numbers = self.importer.get_telephone_numbers_from_row(article, self.row)
        article_category_matrices = self.importer.get_article_category_matrices_from_row(article, self.row)

        rows = [
            {
                "article": article,
                "telephone_numbers": telephone_numbers,
                "article_category_matrices": article_category_matrices,
            }
        ]

        def save_article_category_matrices(article, matrices):
            self.assertEqual(Article.objects.count(), 1)
            self.assertEqual(TelephoneNumber.objects.count(), 2)
            matrices[0] = None
            return self.importer._original_save_article_category_matrices(article, matrices)

        self.importer._original_save_article_category_matrices = self.importer.save_article_category_matrices
        self.importer.save_article_category_matrices = save_article_category_matrices

        expected_exception_msg = "'NoneType' object has no attribute 'article_id'"
        with self.assertRaisesMessage(AttributeError, expected_exception_msg):
            self.importer.save(rows)

        self.assertEqual(Article.objects.count(), 0)
        self.assertEqual(TelephoneNumber.objects.count(), 0)
        self.assertEqual(ArticleCategoryMatrix.objects.count(), 0)

    def _assert_row_telephone(self, row, fields, telephone):
        for column, field_name in fields:
            expected_value = row[column]
            if expected_value == "":
                expected_value = None
            model_value = getattr(telephone, field_name)
            error_msg = "TelephoneNumber.%s expected value %s` got %s instead" % (
                field_name,
                expected_value,
                model_value,
            )
            self.assertEqual(expected_value, model_value, error_msg)

    def _assert_row_against_article(self, row, article):
        for column, field_name in ARTICLE_COLUMN_FIELD_MAPPING:
            expected_value = row[column]
            model_value = getattr(article, field_name)
            if type(model_value) == datetime.datetime:
                model_value = str(model_value)
            error_msg = "Article.%s expected value %s` got %s instead" % (field_name, expected_value, model_value)
            self.assertEqual(expected_value, model_value, error_msg)
