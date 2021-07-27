
from rest_framework import generics, views, pagination, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from discApp.models import Discount
from . import serializers
from .serializers import DiscountShortSerialzier



class ListDiscountApi(generics.ListAPIView):
    """Первичная страница с краткой информацией об акций"""

    # def get_queryset(self):
    #     queryset = Discount.objects.filter(active=True)
    #     return queryset
    queryset = Discount.objects.filter()
    serializer_class = DiscountShortSerialzier
    pagination_class = pagination.LimitOffsetPagination
    filter_backends = [filters.OrderingFilter, filters.SearchFilter, DjangoFilterBackend]
    filter_fields = ['active']
    search_fields = ['category__type', 'description__description']
    ordering_fields =['company__address__city']


class ListDiscountApi2(views.APIView):
    """Страница с полной информации об акциях"""
    def get(self, request, city):
        discounts = Discount.objects.filter(active=True).order_by('id')
        serializer = serializers.DiscountSerialzier(discounts, many=True)
        return Response(serializer.data)

