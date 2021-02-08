import csv
from django.db import transaction
from django.core.exceptions import ValidationError
from knowledgebase.models import Article, TelephoneNumber, ArticleCategoryMatrix
from .csv_user_import_mappings import (
    ARTICLE_COLUMN_FIELD_MAPPING,
    TELEPHONE_COLUMN_FIELD_MAPPING,
    ARTICLE_CATEGORY_MATRIX_COLUMN_FIELD_MAPPING,
)


class KnowledgebaseCSVImporter:
    def parse(self, csv_file_handler):
        rows = []
        errors = []
        reader = csv.reader(csv_file_handler, delimiter=",")
        # Skip header
        next(reader)
        for index, row in enumerate(reader):
            try:
                rows.append(self.process_row(row))
            except ValidationError as e:
                for field, message in e.message_dict.items():
                    errors.append("row %s: %s: %s" % (index + 1, field, message))
            except Exception as e:
                errors.append("row %s: %s" % (index + 1, e.message))
        return [rows, errors]

    def process_row(self, row):
        article = self.get_article_from_row(ARTICLE_COLUMN_FIELD_MAPPING, row)
        telephone_numbers = self.get_telephone_numbers_from_row(article, TELEPHONE_COLUMN_FIELD_MAPPING, row)
        article_category_matrices = self.get_article_category_matrices_from_row(
            article, ARTICLE_CATEGORY_MATRIX_COLUMN_FIELD_MAPPING, row
        )
        return {
            "article": article,
            "telephone_numbers": telephone_numbers,
            "article_category_matrices": article_category_matrices,
        }

    def save(self, rows):
        with transaction.atomic():
            for row in rows:
                row["article"].save()
                self.save_telephone_numbers(row["article"], row["telephone_numbers"])
                self.save_article_category_matrices(row["article"], row["article_category_matrices"])

    def save_telephone_numbers(self, article, telephone_numbers):
        existing_telephone_numbers = TelephoneNumber.objects.filter(article=article)
        if existing_telephone_numbers:
            existing_telephone_numbers.delete()

        for telephone_number in telephone_numbers:
            # Strange this needs to be set explicitly because the telephone_number.article field is already set
            telephone_number.article_id = article.pk
            telephone_number.save()

    def save_article_category_matrices(self, article, matrices):
        existing_matrices = ArticleCategoryMatrix.objects.filter(article=article)
        if existing_matrices:
            existing_matrices.delete()

        for matrix in matrices:
            # Strange this needs to be set explicitly because the matrix.article field is already set
            matrix.article_id = article.pk
            matrix.save()

    def get_article_from_row(self, fields, row):
        data = {}
        pk = None
        for column, field in fields:
            if field == "pk":
                pk = row[column]
            else:
                data[field] = row[column]

        if not data["created"]:
            data.pop("created")
        if not data["modified"]:
            data.pop("modified")

        article = self._get_article_from_pk(pk)
        if article:
            for field, value in data.items():
                setattr(article, field, value)
        else:
            article = Article(**data)

        article.full_clean()
        return article

    def _get_article_from_pk(self, pk):
        if pk == "NEW":
            return None
        try:
            return Article.objects.get(pk=pk)
        except Article.DoesNotExist:
            raise ValueError("Could not find article with an ID of : %s" % pk)

    def get_telephone_numbers_from_row(self, article, mappings, row):
        telephone_numbers = []
        for fields in mappings:
            telephone_number = self.get_telephone_number_from_row(article, fields, row)
            if telephone_number:
                telephone_numbers.append(telephone_number)
        return telephone_numbers

    def get_telephone_number_from_row(self, article, fields, row):
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

    def get_article_category_matrices_from_row(self, article, mappings, row):
        matrices = []
        for fields in mappings:
            matrix = self.get_get_article_category_matrix_from_row(article, fields, row)
            if matrix:
                matrices.append(matrix)
        return matrices

    def get_get_article_category_matrix_from_row(self, article, fields, row):
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
