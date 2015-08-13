# -*- coding: utf-8 -*-
from rest_framework import mixins, viewsets
from core.drf.mixins import FormActionMixin

from .models import Complaint, Category
from .serializers import ComplaintSerializerBase, CategorySerializerBase


class ComplaintFormActionMixin(FormActionMixin):
    """
    This is for backward compatibility
    """
    FORM_ACTION_OBJ_PARAM = 'complaint'


class BaseComplaintViewSet(
    ComplaintFormActionMixin,
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
