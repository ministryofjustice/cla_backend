# -*- coding: utf-8 -*-
from rest_framework import viewsets
from rest_framework import filters

from .models import Note
from .serializers import NoteSerializer


class PostgresFullTextSearchFilter(filters.BaseFilterBackend):
    search_param = filters.api_settings.SEARCH_PARAM

    def filter_queryset(self, request, queryset, view):
        if not hasattr(queryset, 'search'):
            return queryset
        return queryset.search(request.QUERY_PARAMS.get(self.search_param, ''))


class BaseGuidanceNoteViewSet(viewsets.ReadOnlyModelViewSet):
    model = Note
    serializer_class = NoteSerializer

    filter_backends = (PostgresFullTextSearchFilter,)
