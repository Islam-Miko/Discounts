import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from discounts.models import ClientDiscount

from .factories import ClientDiscountFactory, DiscountLimitFactory

pytestmark = pytest.mark.django_db


class TestCouponAPIView:
    endpoint_url = "coupon-create"

    def test_coupon_creation(self, base_client: APIClient, user, one_discount):
        url = reverse(self.endpoint_url, kwargs={"pk": one_discount.id})

        DiscountLimitFactory(discount=one_discount)
        base_client.force_authenticate(user)
        assert not ClientDiscount.objects.filter(
            client=user,
            discount=one_discount,
            status=ClientDiscount.STATUSES.BOOKED,
        ).exists()
        response = base_client.post(url)
        assert response.status_code == status.HTTP_201_CREATED
        assert ClientDiscount.objects.filter(
            client=user,
            discount=one_discount,
            status=ClientDiscount.STATUSES.BOOKED,
        ).exists()

    def test_user_has_coupon(self, base_client: APIClient, user, discount):
        ClientDiscountFactory(
            client=user,
            discount=discount,
            status=ClientDiscount.STATUSES.BOOKED,
        )
        base_client.force_authenticate(user)
        url = reverse(self.endpoint_url, kwargs={"pk": discount.id})
        response = base_client.post(url)
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.data["detail"] == "Already have a coupon!"
