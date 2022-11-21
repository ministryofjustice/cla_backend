import django_filters
from rest_framework import viewsets
from rest_framework import filters

from .models import Article, ArticleCategory
from .serializers import ArticleSerializer, ArticleCategorySerializer


class ArticleCategoryFilter(django_filters.FilterSet):
    article_category = django_filters.ModelMultipleChoiceFilter

    class Meta(object):
        # Todo: is queryset needed
        queryset = Article.objects.all()
        model = Article
        fields = ("article_category",)


class BaseArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Article.objects.all()
    model = Article
    serializer_class = ArticleSerializer

    paginate_by = 20
    paginate_by_param = "page_size"
    max_paginate_by = 100

    filter_backends = (filters.SearchFilter, filters.DjangoFilterBackend, filters.OrderingFilter)

    filter_class = ArticleCategoryFilter

    ordering = ("-articlecategorymatrix__preferred_signpost",)

    search_fields = (
        "organisation",
        "service_name",
        "description",
        "keywords",
        "when_to_use",
        "type_of_service",
        "address",
        "article_category__name",
    )


class BaseArticleCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ArticleCategory.objects.all()
    model = ArticleCategory
    serializer_class = ArticleCategorySerializer
