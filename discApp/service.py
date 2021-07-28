from rest_framework import filters
from collections import deque


from rest_framework.settings import api_settings


class ByCityFilterBackend(filters.BaseFilterBackend):
    search_param = api_settings.SEARCH_PARAM

    def get_search_terms(self, request):
        """
        Search terms are set by a ?search=... query parameter,
        and may be comma and/or whitespace delimited.
        """
        params = request.query_params.get('city', '')
        params = params.replace('\x00', '')  # strip null characters
        params = params.replace(',', ' ')
        return params

    def filter_queryset(self, request, queryset, view):

        search_terms = self.get_search_terms(request)
        print(search_terms)
        if not search_terms:
            return queryset

        result = deque()
        print(len(queryset))
        # need = queryset.filter(company__addresses__city=search_terms)
        # notneet = queryset.exclude(company__addresses__city=search_terms)
        for query in queryset:
            print(type(query.company.city))
            if str(query.company.city) == search_terms:
                result.appendleft(query)
            else:
                result.append(query)

        return result
