from django.urls import path
from . import views
urlpatterns = [
    path('discounts/<int:pk>', views.ListDiscountApi2.as_view()),
    path('discounts', views.ListDiscountApi.as_view()),
    path('review', views.CreateReviewApi.as_view()),
    path('coupon/<int:pk>/<int:client>', views.RetrieveCouponView.as_view()),
    path('clientdiscount', views.ListApi.as_view()),
]