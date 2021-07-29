import datetime

from rest_framework import filters
from collections import deque

from rest_framework.response import Response
from rest_framework.settings import api_settings
from . import models

class ByCityFilterBackend(filters.BaseFilterBackend):
    """Кастомный фильтр по городам"""
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
        for query in queryset:
            if str(query.company.city) == search_terms:
                result.appendleft(query)
            else:
                result.append(query)

        return result


def mark_coupon_creation(discount, client):
    today = datetime.datetime.today()
    day_48_hours_ago = today - datetime.timedelta(days=2)

    day_use_of_discount = models.ClientDiscount.objects.filter(add_date__day=datetime.datetime.today().day,
                                                                 discount=discount).count()
    total_uses_of_discount = models.ClientDiscount.objects.filter(status='ACTIVATED',
                                                                  discount=discount).count()
    day_limit = models.DiscountLimit.objects.filter(discount=discount).get().day_limit
    total_limit = models.DiscountLimit.objects.filter(discount=discount).get().total_limit

    if day_use_of_discount == day_limit or total_uses_of_discount == total_limit:
        return True

    models.ClientDiscount.objects.filter(add_date__gte=day_48_hours_ago).get_or_create(discount=discount,
                                                                                        client=client)




