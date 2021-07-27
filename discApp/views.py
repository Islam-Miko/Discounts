
from rest_framework import generics, views, pagination, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from discApp.models import Discount

from .serializers import DiscountShortSerialzier, DiscountSerialzier



class ListDiscountApi(generics.ListAPIView):
    """Первичная страница с краткой информацией об акций"""

    # def get_queryset(self):
    #     queryset = Discount.objects.filter(active=True)
    #     return queryset
    queryset = Discount.objects.all()
    serializer_class = DiscountShortSerialzier
    pagination_class = pagination.LimitOffsetPagination
    filter_backends = [filters.OrderingFilter, filters.SearchFilter, DjangoFilterBackend]
    filter_fields = ['active']
    search_fields = ['category__type', 'description__description']
    ordering_fields =['company__address__city']


class ListDiscountApi2(generics.RetrieveAPIView):
    """Страница с полной информации об акции"""

    queryset = Discount.objects.all()
    serializer_class = DiscountSerialzier

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.increment()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)




