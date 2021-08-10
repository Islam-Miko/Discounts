from django.urls import path
from . import views
urlpatterns = [
    path('discounts/<int:pk>', views.ListDiscountApi2.as_view()),
    # Детальный просмотр акции
    path('discounts', views.ListDiscountApi.as_view()),
    #  просмотр краткой информации об акциях
    path('review', views.CreateReviewApi.as_view()),
    # написания отзыва к акции
    path('coupon', views.CouponView.as_view()),
    # получение купона
    path('coupon/activate', views.CouponActivate.as_view()),
    # активация купона
    path('categories', views.CategoryView.as_view()),
    # получение купона

]