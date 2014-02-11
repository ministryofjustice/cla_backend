from rest_framework import status
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Category, EligibilityCheck
from .serializers import CategorySerializer, EligibilityCheckSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    model = Category
    serializer_class = CategorySerializer


class EligibilityCheckViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    model = EligibilityCheck
    serializer_class = EligibilityCheckSerializer

    lookup_field = 'reference'
    pk_url_kwarg = 'reference'
