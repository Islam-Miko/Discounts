
from rest_framework import generics, pagination, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from discApp.models import Discount, Review

from .serializers import DiscountShortSerialzier, DiscountSerialzier, ReviewSerializer
from .service import ByCityFilterBackend


class ListDiscountApi(generics.ListAPIView):
    """Первичная страница с краткой информацией об акций"""

    queryset = Discount.objects.all().order_by('company__addresses__city__order_num', 'order_num')
    serializer_class = DiscountShortSerialzier
    pagination_class = pagination.LimitOffsetPagination
    filter_backends = [filters.OrderingFilter, filters.SearchFilter, DjangoFilterBackend, ByCityFilterBackend]
    filter_fields = ['active']
    search_fields = ['category__type', 'description__description',]


class ListDiscountApi2(generics.RetrieveAPIView):
    """Страница с полной информации об акции"""

    queryset = Discount.objects.all()
    serializer_class = DiscountSerialzier

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.increment()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class CreateReviewApi(generics.CreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


# class ListDiscountApi3(generics.ListAPIView):
#     """Страница с полной информации об акции"""
#
#     queryset = Discount.objects.all()
#     serializer_class = DiscountSerialzier4




