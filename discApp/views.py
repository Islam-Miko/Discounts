import datetime

from rest_framework import generics, pagination, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from discApp.models import Discount, Review, Client, ClientDiscount, DiscountLimit

from .serializers import DiscountShortSerialzier, DiscountSerialzierDto, ReviewSerializer, CouponSerializer
from . import service
from .dtos import discountDtoWhole, couponDto


class ListDiscountApi(generics.ListAPIView):
    """Первичная страница с краткой информацией об акций"""

    queryset = Discount.objects.all().order_by('company__addresses__city__order_num', 'order_num')
    serializer_class = DiscountShortSerialzier
    pagination_class = pagination.LimitOffsetPagination
    filter_backends = [filters.OrderingFilter, filters.SearchFilter, DjangoFilterBackend, service.ByCityFilterBackend]
    filter_fields = ['active']
    search_fields = ['category__type',]
    ordering_fields = ['order_num']


class ListDiscountApi2(generics.RetrieveAPIView):
    """Страница с полной информации об акции"""

    queryset = Discount.objects.all()
    serializer_class = DiscountSerialzierDto

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.increment()
        instance = discountDtoWhole(instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class CreateReviewApi(generics.CreateAPIView):
    """Создание отзыва к акции"""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class RetrieveCouponView(generics.RetrieveAPIView):
    queryset = Discount.objects.all()
    serializer_class = CouponSerializer

    def get(self, request, *args, **kwargs):
        disc_obj = self.get_object()
        client = Client.objects.last()
        limits_are_reached = service.mark_coupon_creation(disc_obj, client)
        if limits_are_reached:
            return Response('you cannot')
        return self.retrieve(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        client = Client.objects.last()
        instance = couponDto(instance, client)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)




