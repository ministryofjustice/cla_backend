from django.contrib.postgres.search import SearchVector, SearchQuery
from rest_framework.filters import BaseFilterBackend
from rest_framework.settings import api_settings


class SearchVectorFilter(BaseFilterBackend):
    # The URL query parameter used for the search.
    search_param = api_settings.SEARCH_PARAM
    search_config = 'simple'

    def get_search_terms(self, request):
        """
        Search terms are set by a ?search=... query parameter,
        and may be comma and/or whitespace delimited.
        """
        params = request.QUERY_PARAMS.get(self.search_param, '')
        return params.replace(',', ' ').split()

    def filter_queryset(self, request, queryset, view):
        search_fields = getattr(view, 'search_vector_fields', None)

        if not search_fields:
            return queryset

        search_vector = SearchVector(*search_fields, config=self.search_config)
        queryset = queryset.annotate(search_vector)

        for search_term in self.get_search_terms(request):
            queryset = queryset.filter(
                search=SearchQuery(search_term, config=self.search_config)
            )

        return queryset
