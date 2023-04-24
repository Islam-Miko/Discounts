from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import CharField, F, Value
from django.db.models.functions import Concat, JSONObject
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import filters, generics, pagination, status, views
from rest_framework.response import Response

from discounts.models import Category, Client, ClientDiscount, Discount, Review

from . import filters as custom_filters
from . import service
from .decorators import increment_views
from .dtos import couponDto
from .serializers import (
    CategorySerialzir,
    CouponSerializer,
    DiscountFullInformationSerializer,
    DiscountShortInformationSerializer,
    PincodeValidationSerialzier,
    ReviewSerializer,
)


class DiscountListAPIView(generics.ListAPIView):
    """
    APIView for all active Discounts
    """

    queryset = (
        Discount.objects.filter(
            active=True,
            deleted_at__isnull=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now(),
        )
        .select_related("company", "category", "instruction")
        .order_by("company__addresses__city__order_num", "order_num")
    )
    serializer_class = DiscountShortInformationSerializer
    pagination_class = pagination.LimitOffsetPagination
    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
        custom_filters.PriorityOrderFilter,
    ]
    ordering_fields = ["order_num"]
    search_fields = ["category__id"]
    priority_field = "company__addresses__city"


class DiscountDetailAPIView(generics.RetrieveAPIView):
    """APIView for detail view for Discount"""

    serializer_class = DiscountFullInformationSerializer

    def get_queryset(self):
        queryset = (
            Discount.objects.filter(active=True)
            .select_related(
                "description", "views", "company", "instruction", "category"
            )
            .annotate(
                views_count=F("views__amount"),
                discount_city=F("company__addresses__city__city"),
                addres=Concat(
                    F("company__addresses__street"),
                    Value(" "),
                    F("company__addresses__house"),
                    output_field=CharField(),
                ),
                company_phones=ArrayAgg(F("company__phones__phone")),
                company_socials=ArrayAgg(
                    JSONObject(
                        url=F("company__socials__url"),
                        type=F("company__socials__type"),
                        logo=F("company__socials__logo"),
                    )
                ),
            )
        )
        return queryset

    @method_decorator(increment_views)
    @method_decorator(cache_page(60))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class CreateReviewApi(generics.CreateAPIView):
    """Создание отзыва к акции"""

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class CouponView(views.APIView):
    """Для получения купона"""

    def post(self, request):
        try:
            discount = service.get_object_by_id(
                Discount, self.request.query_params.get("discount")
            )
            client = service.get_object_by_id(
                Client, self.request.query_params.get("client")
            )
        except Client.DoesNotExist:
            return Response(
                {"Message": "Client Not Found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Discount.DoesNotExist:
            return Response(
                {"Message": "Discount Not Found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        limits_are_reached, message = service.coupon_creation(discount, client)
        if limits_are_reached:
            return Response(f"{message}")
        instance = couponDto(discount, client)
        serializer = CouponSerializer(instance)
        return Response(serializer.data)


class CouponActivate(views.APIView):
    """Для активации купона"""

    def post(self, request):
        try:
            discount = service.get_object_by_id(
                Discount, self.request.query_params.get("discount")
            )
            client = service.get_object_by_id(
                Client, self.request.query_params.get("client")
            )
        except Client.DoesNotExist:
            return Response(
                {"Message": "Client Not Found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Discount.DoesNotExist:
            return Response(
                {"Message": "Discount Not Found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        pincode = PincodeValidationSerialzier(data=request.data)
        pincode.is_valid(raise_exception=True)

        instance_to_status_change = service.find_last_BOOKED_object_of_client(
            discount, client
        )
        if instance_to_status_change:
            if discount.pincode == pincode.data.get("pincode"):
                instance_to_status_change.status = ClientDiscount.STATUS[2][0]
                instance_to_status_change.save()
                return Response({"message": "Successful", "ok": True})
            return Response(
                {"message": "invalid pincode", "ok": False},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"No coupon Im sorry"})


class CategoryView(generics.ListAPIView):
    queryset = Category.objects.order_by("order_num").all()
    serializer_class = CategorySerialzir
