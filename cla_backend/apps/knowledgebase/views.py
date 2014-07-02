from rest_framework import viewsets
#from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework import filters

from .models import Article, ArticleCategory
from .serializers import ArticleSerializer, ArticleCategorySerializer
from call_centre.views import CallCentrePermissionsViewSetMixin


class ArticleViewSet(
        CallCentrePermissionsViewSetMixin,
        viewsets.ReadOnlyModelViewSet):
    model = Article
    serializer_class = ArticleSerializer

    filter_backends = (
        filters.SearchFilter,
        filters.DjangoFilterBackend
    )

    filter_fields = ('article_category',)

    search_fields = ('organisation', 'service_name', 'description',
                     'keywords', 'when_to_use', 'type_of_service',
                     'address', 'article_category__name')


class ArticleCategoryViewSet(
        CallCentrePermissionsViewSetMixin,
        viewsets.ReadOnlyModelViewSet):
    model = ArticleCategory
    serializer_class = ArticleCategorySerializer
