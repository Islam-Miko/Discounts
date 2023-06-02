from django.urls import path

from . import views

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
    path("discounts/<int:pk>/coupon", views.CouponCreateAPIView.as_view()),
    # получение купона
    path("coupon/activate", views.CouponActivate.as_view()),
    # активация купона
    path("categories", views.CategoryView.as_view()),
    # получение купона
]
