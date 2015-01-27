from rest_framework import serializers

from .models import Article, ArticleCategoryMatrix, ArticleCategory, \
    TelephoneNumber


class ArticleCategoryMatrixSerializer(serializers.ModelSerializer):
    id = serializers.Field(source='article_category.pk')
    name = serializers.Field(source='article_category.name')
    preferred_signpost = serializers.Field(source='preferred_signpost')

    class Meta:
        model = ArticleCategoryMatrix
        fields = ('id', 'name', 'preferred_signpost')


class TelephoneNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelephoneNumber
        exclude = ('id', 'article', 'created', 'modified')


class ArticleSerializer(serializers.ModelSerializer):
    categories = ArticleCategoryMatrixSerializer(
        source='articlecategorymatrix_set', many=True)
    telephone_numbers = TelephoneNumberSerializer(
        source='telephonenumber_set', many=True)

    class Meta:
        model = Article
        exclude = ('article_category',)


class ArticleCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleCategory
        exclude = ('created', 'modified')
