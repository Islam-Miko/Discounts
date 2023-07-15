import datetime

from django.contrib.auth import get_user_model
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import (
    CharField,
    DateTimeField,
    ExpressionWrapper,
    F,
    Value,
)
from django.db.models.functions import Concat, JSONObject
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.utils import extend_schema
from rest_framework import filters, generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response

from discounts.models import ClientDiscount, Discount, Review

from . import filters as custom_filters
from . import service
from .decorators import increment_views
from .serializers import (
    CouponCreateSerializer,
    CouponGetSerializer,
    DiscountFullInformationSerializer,
    DiscountShortInformationSerializer,
    ReviewSerializer,
    SuccessfulResponseSerializer,
)

Client = get_user_model()


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


class CouponCreateAPIView(generics.CreateAPIView):
    serializer_class = CouponCreateSerializer

    @extend_schema(
        request=None,
        description="Endpoint to get coupon. No request body required",
    )
    def post(self, request, pk: int, *args, **kwargs):
        service.check_conditions(pk, request.user)
        return super().post(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=dict(
                discount=self.kwargs.get(self.lookup_field),
                client=request.user.id,
            ),
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        coupon = service.get_coupon(serializer.data.get("id"))
        serializer = CouponGetSerializer(coupon)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class CouponAPIView(
    ListModelMixin, RetrieveModelMixin, viewsets.GenericViewSet
):
    serializer_class = CouponGetSerializer

    def get_queryset(self):
        return ClientDiscount.objects.annotate(
            company=F("discount__company__name"),
            image=F("discount__company__image"),
            description=F("discount__description__description"),
            percentage=F("discount__percentage"),
            valid_time=ExpressionWrapper(
                F("add_date") + datetime.timedelta(days=2),
                output_field=DateTimeField(),
            ),
        )

    @extend_schema(
        request=None,
        responses={status.HTTP_200_OK: SuccessfulResponseSerializer},
    )
    @action(detail=True, url_path=r"activate", methods=["patch"])
    def activate_coupon(self, request, pk: str):
        service.activate_coupon(pk)
        return Response({"message": "Ok"})
