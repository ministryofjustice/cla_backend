from rest_framework import serializers

from .models import Article, ArticleCategoryMatrix


class ArticleCategoryMatrixSerializer(serializers.ModelSerializer):
    id = serializers.Field(source='article_category.pk')
    name = serializers.Field(source='article_category.name')
    preferred_signpost = serializers.Field(source='preferred_signpost')

    class Meta:
        model = ArticleCategoryMatrix
        fields = ('id', 'name', 'preferred_signpost')


class ArticleSerializer(serializers.ModelSerializer):
    categories = ArticleCategoryMatrixSerializer(
        source='articlecategorymatrix_set', many=True)

    class Meta:
        model = Article
        exclude = ('article_category',)
