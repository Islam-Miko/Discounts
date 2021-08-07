import datetime

from rest_framework import generics, pagination, filters, status, views
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from discApp.models import Discount, Review, Client, ClientDiscount
from .serializers import (DiscountSerialzierDto, ReviewSerializer,
                          CouponSerializer, DiscountSerialzierDtoShort,
                          ClientDiscountSerializer, PincodeValidationSerialzier)

from . import service
from .dtos import discountDtoWhole, couponDto
from .service import make_list_dto, get_object_by_id, find_last_BOOKED_object_of_client


class ListDiscountApi(generics.ListAPIView):
    """Первичная страница с краткой информацией об акций"""

    queryset = Discount.objects.filter(active=True,
                                       start_date__lte=datetime.datetime.today(),
                                       end_date__gte=datetime.datetime.today()).order_by('company__addresses__city__order_num', 'order_num')
    serializer_class = DiscountSerialzierDtoShort
    pagination_class = pagination.LimitOffsetPagination
    filter_backends = [filters.OrderingFilter, filters.SearchFilter, service.ByCityFilterBackend]
    # filter_fields = ['active']
    search_fields = ['category__type',]
    ordering_fields = ['order_num']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = make_list_dto(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ListDiscountApi2(generics.RetrieveAPIView):
    """Страница с полной информации об акции"""

    queryset = Discount.objects.filter(active=True).all()
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


# # class RetrieveCouponView(views.APIView):
#
#     def get(self, request, pk, client):
#         try:
#             disc_obj = Discount.objects.filter(id=pk).get()
#             client = Client.objects.filter(id=client).get()
#         except (Client.DoesNotExist, Discount.DoesNotExist):
#             return Response({'Message':'Not Found'}, status=status.HTTP_404_NOT_FOUND)
#         limits_are_reached, message = service.coupon_creation(disc_obj, client)
#         if limits_are_reached:
#             return Response(f'{message}')
#         instance = couponDto(disc_obj, client)
#         serializer = CouponSerializer(instance)
#         return Response(serializer.data)
#
#     # def put(self, request, pk, client):
#     #     data = request.data
#     #     try:
#     #         disc_obj = Discount.objects.filter(id=pk).get()
#     #         client = Client.objects.filter(id=client).get()
#     #         instance = ClientDiscount.objects.filter(discount=disc_obj,
#     #                                                  client=client).last()
#     #     except (Client.DoesNotExist, Discount.DoesNotExist):
#     #         return Response({'Message':'Discount or CLient Not Found'}, status=status.HTTP_404_NOT_FOUND)
#     #     serializer = ClientDiscountSerializer(instance, data=data)
#     #     if serializer.is_valid(raise_exception=True):
#     #         serializer.save()
#     #         return Response({"Message":" Succesful"})
#
#     def put(self, request, pk, client):
#         try:
#             discount = Discount.objects.filter(id=pk).get()
#             client = Client.objects.filter(id=client).get()
#
#         except (Client.DoesNotExist, Discount.DoesNotExist):
#             return Response({'Message': 'Discount or CLient Not Found'}, status=status.HTTP_404_NOT_FOUND)
#
#         pincode = PincodeValidationSerialzier(data=request.data)
#         pincode.is_valid(raise_exception=True)
#
#
#         instance_to_status_change = ClientDiscount.objects.filter(discount=discount,
#                                                                   client=client, status='BOOKED').last()
#         if instance_to_status_change:
#             if discount.pincode == pincode.data.get('pincode'):
#                 instance_to_status_change.status = ClientDiscount.STATUS[2][0]
#                 instance_to_status_change.save()
#                 return Response({"message":"Successful"})
#             return Response({"message":"invalid pincode"}, status=status.HTTP_400_BAD_REQUEST)
#         return Response({"No coupon Im sorry"})


class ListApi(generics.ListAPIView):
    queryset = ClientDiscount.objects.all()
    serializer_class = ClientDiscountSerializer


class CouponView(views.APIView):

    def post(self, request):
        try:
            disc_obj = get_object_by_id(Discount, self.request.query_params.get('discount'))
            client = get_object_by_id(Client, self.request.query_params.get('client'))
        except (Client.DoesNotExist, Discount.DoesNotExist):
            return Response({'Message':'Not Found'}, status=status.HTTP_404_NOT_FOUND)
        limits_are_reached, message = service.coupon_creation(disc_obj, client)
        if limits_are_reached:
            return Response(f'{message}')
        instance = couponDto(disc_obj, client)
        serializer = CouponSerializer(instance)
        return Response(serializer.data)


class CouponActivate(views.APIView):
    def post(self, request):
        try:
            discount = get_object_by_id(Discount, self.request.query_params.get('discount'))
            client = get_object_by_id(Client, self.request.query_params.get('client'))

        except Client.DoesNotExist:
            return Response({'Message': 'CLient Not Found'}, status=status.HTTP_404_NOT_FOUND)
        except Discount.DoesNotExist:
            return Response({'Message': 'Discount Not Found'}, status=status.HTTP_404_NOT_FOUND)

        pincode = PincodeValidationSerialzier(data=request.data)
        pincode.is_valid(raise_exception=True)

        instance_to_status_change = find_last_BOOKED_object_of_client(discount, client)
        if instance_to_status_change:
            if discount.pincode == pincode.data.get('pincode'):
                instance_to_status_change.status = ClientDiscount.STATUS[2][0]
                instance_to_status_change.save()
                return Response({"message":"Successful"})
            return Response({"message":"invalid pincode"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"No coupon Im sorry"})


