from uuid import UUID
from django import http
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Category, EligibilityCheck, Property
from .serializers import CategorySerializer, EligibilityCheckSerializer, PropertySerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    model = Category
    serializer_class = CategorySerializer


class EligibilityCheckViewSet(
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        viewsets.GenericViewSet
    ):
    model = EligibilityCheck
    serializer_class = EligibilityCheckSerializer

    lookup_field = 'reference'


class NestedModelMixin(object):

    parent_model = None
    parent_lookup = None
    nested_lookup = None

    @csrf_exempt
    def dispatch(self, request,  *args, **kwargs):
        key = kwargs['{parent_lookup}__{lookup}'.\
            format(parent_lookup=self.parent_lookup, lookup=self.nested_lookup)]

        self.parent_instance = get_object_or_404(
            self.parent_model, **{self.nested_lookup: key})

        return super(NestedModelMixin, self).dispatch(request, *args, **kwargs)


    def get_queryset(self):
        qs = super(NestedModelMixin, self).get_queryset()
        return qs.filter(**{self.parent_lookup: self.parent_instance})

    def pre_save(self, obj):
        setattr(obj, self.parent_lookup, self.parent_instance)
        super(NestedModelMixin, self).pre_save(obj)


class PropertyViewSet(
    NestedModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
    ):

    nested_lookup = 'reference'
    parent_lookup = 'eligibility_check'
    parent_model = EligibilityCheck


    model = Property
    serializer_class = PropertySerializer
