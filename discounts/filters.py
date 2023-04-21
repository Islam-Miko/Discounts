from rest_framework import filters
from django.db import models
import itertools

class PriorityOrderFilter(filters.BaseFilterBackend):
    priority_param = "city_id"

    def get_priority_term(self, request):
        """
        Priority term is set by a ?city_id=... query parameter,
        and may be comma and/or whitespace delimited.
        """
        params = request.query_params.get(self.priority_param, '')
        params = params.replace('\x00', '')  # strip null characters
        params = params.replace(',', ' ')
        return params
    
    def get_priority_field(self, view, request):
        """
        Priority field is obtained from the view, but the request is always
        passed to this method. Sub-classes can override this method to
        dynamically change the priority field based on request content.
        """
        return getattr(view, 'priority_field', None)

    def filter_queryset(self, request, queryset, view):
        priority_term = self.get_priority_term(request)
        priority_field = self.get_priority_field(view, request)
        if not priority_term or not priority_field:
            return queryset
        needed_cities = queryset.filter(models.Q(**{priority_field: priority_term}))
        rest_cities = queryset.filter(~models.Q(**{priority_field: priority_term}))
        return itertools.chain(needed_cities, rest_cities)