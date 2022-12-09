# coding=utf-8
from rest_framework import viewsets
from rest_framework import filters

from .models import Note
from .serializers import NoteSerializer, NoteSearchSerializer


class PostgresFullTextSearchFilter(filters.BaseFilterBackend):
    search_param = filters.api_settings.SEARCH_PARAM

    def filter_queryset(self, request, queryset, view):
        q = request.query_params.get(self.search_param, "")
        if q:
            queryset = queryset.word_tree_search(q)
        return queryset


class BaseGuidanceNoteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Note.objects.all()
    model = Note
    lookup_field = "name"

    filter_backends = (PostgresFullTextSearchFilter,)

    def serializer_class(self, *args, **kwargs):
        if kwargs.get("many", None):
            return NoteSearchSerializer(*args, **kwargs)
        else:
            return NoteSerializer(*args, **kwargs)
