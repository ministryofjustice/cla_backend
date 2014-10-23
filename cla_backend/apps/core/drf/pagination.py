from rest_framework.templatetags.rest_framework import replace_query_param
from rest_framework.pagination import BasePaginationSerializer
from rest_framework import serializers


class RelativeNextPageField(serializers.Field):
    page_field = 'page'

    def to_native(self, value):
        if not value.has_next():
            return None
        page = value.next_page_number()
        return replace_query_param('', self.page_field, page)


class RelativePreviousPageField(serializers.Field):
    page_field = 'page'

    def to_native(self, value):
        if not value.has_previous():
            return None
        page = value.previous_page_number()
        return replace_query_param('', self.page_field, page)


class RelativeUrlPaginationSerializer(BasePaginationSerializer):
    count = serializers.Field(source='paginator.count')
    next = RelativeNextPageField('*')
    previous = RelativePreviousPageField('*')
