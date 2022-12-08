from rest_framework.templatetags.rest_framework import replace_query_param
from rest_framework.pagination import PageNumberPagination
from rest_framework import serializers


class RelativeNextPageField(serializers.ReadOnlyField):
    page_field = "page"

    def to_representation(self, value):
        if not value.has_next():
            return None
        page = value.next_page_number()
        return replace_query_param("", self.page_field, page)


class RelativePreviousPageField(serializers.ReadOnlyField):
    page_field = "page"

    def to_representation(self, value):
        if not value.has_previous():
            return None
        page = value.previous_page_number()
        return replace_query_param("", self.page_field, page)


class RelativeUrlPaginationSerializer(PageNumberPagination):
    count = serializers.ReadOnlyField(source="paginator.count")
    next = RelativeNextPageField(source="*")
    previous = RelativePreviousPageField(source="*")
