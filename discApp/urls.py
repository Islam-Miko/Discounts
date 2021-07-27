from django.urls import path
from . import views
urlpatterns = [
    path('discounts/detail', views.ListDiscountApi2.as_view()),
    path('discounts', views.ListDiscountApi.as_view()),
]