# -*- coding: utf-8 -*-
from rest_framework import mixins, viewsets

from .models import Complaint, Category
from .serializers import ComplaintSerializerBase, CategorySerializerBase


class BaseComplaintViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    model = Complaint
    serializer_class = ComplaintSerializerBase


class BaseComplaintCategoryViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    model = Category
    serializer_class = CategorySerializerBase
