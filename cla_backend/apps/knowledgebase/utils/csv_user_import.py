import csv
from django.db import transaction
from knowledgebase.models import Article, TelephoneNumber, ArticleCategoryMatrix
from .csv_user_import_mappings import (
    ARTICLE_COLUMN_FIELD_MAPPING,
    TELEPHONE_COLUMN_FIELD_MAPPING,
    ARTICLE_CATEGORY_MATRIX_COLUMN_FIELD_MAPPING,
)


class KnowledgebaseCSVImporter:
    @classmethod
    def parse(cls, csv_file_handler):
        rows = []
        errors = []
        reader = csv.reader(csv_file_handler, delimiter=",")
        # Skip header
        next(reader)
        for index, row in enumerate(reader):
            try:
                rows.append(cls.process_row(row))
            except Exception as e:
                errors.append("row %s: %s" % (index + 1, e.message))
        return [rows, errors]

    @classmethod
    def process_row(cls, row):
        article = cls.get_article_from_row(ARTICLE_COLUMN_FIELD_MAPPING, row)
        telephone_numbers = cls.get_telephone_numbers_from_row(article, TELEPHONE_COLUMN_FIELD_MAPPING, row)
        article_category_matrices = cls.get_get_article_category_matrices_from_row(
            article, ARTICLE_CATEGORY_MATRIX_COLUMN_FIELD_MAPPING, row
        )
        return {
            "article": article,
            "telephone_numbers": telephone_numbers,
            "article_category_matrices": article_category_matrices,
        }

    @classmethod
    def save(cls, rows):
        with transaction.atomic():
            for row in rows:
                row["article"].save()
                cls.save_telephone_numbers(row["article"], row["telephone_numbers"])
                cls.save_article_category_matrices(row["article"], row["article_category_matrices"])

    @classmethod
    def save_telephone_numbers(cls, article, telephone_numbers):
        existing_telephone_numbers = TelephoneNumber.objects.filter(article=article)
        if existing_telephone_numbers:
            existing_telephone_numbers.delete()

        for telephone_number in telephone_numbers:
            # Strange this needs to be set explicitly because the telephone_number.article field is already set
            telephone_number.article_id = article.pk
            telephone_number.save()

    @classmethod
    def save_article_category_matrices(cls, article, matrices):
        existing_matrices = ArticleCategoryMatrix.objects.filter(article=article)
        if existing_matrices:
            existing_matrices.delete()

        for matrix in matrices:
            # Strange this needs to be set explicitly because the matrix.article field is already set
            matrix.article_id = article.pk
            matrix.save()

    @classmethod
    def get_article_from_row(cls, fields, row):
        data = {}
        pk = None
        for column, field in fields:
            if field == "pk":
                pk = row[column]
            else:
                data[field] = row[column]

        article = cls._get_article_from_pk(pk)
        if article:
            for field, value in data.items():
                setattr(article, field, value)
        else:
            article = Article(**data)

        article.full_clean()
        return article

    @classmethod
    def _get_article_from_pk(cls, pk):
        if pk == "NEW":
            return None

        if not type(pk, int):
            raise ValueError("ID must be an existing ID or NEW. Value given %s" % pk)
        try:
            return Article.objects.get(pk=pk)
        except Article.DoesNotExist:
            raise ValueError("Could not find article with an ID of : %s" % pk)

    @classmethod
    def get_telephone_numbers_from_row(cls, article, mappings, row):
        telephone_numbers = []
        for fields in mappings:
            telephone_number = cls.get_telephone_number_from_row(article, fields, row)
            if telephone_number:
                telephone_numbers.append(telephone_number)
        return telephone_numbers

    @classmethod
    def get_telephone_number_from_row(cls, article, fields, row):
        data = {}
        telephone_number = None
        for column, field in fields:
            if row[column]:
                data[field] = row[column]
        if data:
            data["article"] = article
            telephone_number = TelephoneNumber(**data)
            telephone_number.full_clean(exclude=["article"])
        return telephone_number

    @classmethod
    def get_get_article_category_matrices_from_row(cls, article, mappings, row):
        matrices = []
        for fields in mappings:
            matrix = cls.get_get_article_category_matrix_from_row(article, fields, row)
            if matrix:
                matrices.append(matrix)
        return matrices

    @classmethod
    def get_get_article_category_matrix_from_row(cls, article, fields, row):
        data = {}
        matrix = None
        for column, field, value_transformer in fields:
            if row[column]:
                data[field] = value_transformer(row[column])
        if data:
            data["article"] = article
            matrix = ArticleCategoryMatrix(**data)
            matrix.full_clean(exclude=["article"])
        return matrix
