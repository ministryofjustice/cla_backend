from core.drf.mixins import NestedGenericModelMixin
from diagnosis.models import DiagnosisTraversal
from diagnosis.serializers import DiagnosisSerializer
from django.shortcuts import render
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action, link
from rest_framework.response import Response


class BaseDiagnosisViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    NestedGenericModelMixin,
    viewsets.GenericViewSet
    ):

    serializer_class = DiagnosisSerializer
    PARENT_FIELD = 'diagnosis'
    model = DiagnosisTraversal
    lookup_field = 'reference'

