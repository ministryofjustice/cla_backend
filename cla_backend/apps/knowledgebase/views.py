from rest_framework import viewsets

from .models import Article
from .serializers import ArticleSerializer
from call_centre.views import CallCentrePermissionsViewSetMixin


class ArticleViewSet(
    CallCentrePermissionsViewSetMixin,
    viewsets.ReadOnlyModelViewSet):
    model = Article
    serializer_class = ArticleSerializer
