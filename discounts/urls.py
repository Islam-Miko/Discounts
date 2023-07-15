from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"coupons", views.CouponAPIView, basename="coupons")


urlpatterns = [
    path(
        "discounts/<int:pk>",
        views.DiscountDetailAPIView.as_view(),
        name="discount-detail",
    ),
    # Детальный просмотр акции
    path(
        "discounts", views.DiscountListAPIView.as_view(), name="discount-list"
    ),
    #  просмотр краткой информации об акциях
    path("review", views.CreateReviewApi.as_view()),
    # написания отзыва к акции
    path(
        "discounts/<int:pk>/coupon",
        views.CouponCreateAPIView.as_view(),
        name="coupon-create",
    ),
    # получение купона
] + router.urls
