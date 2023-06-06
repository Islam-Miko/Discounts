import pytest
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from discounts.models import Discount

from .factories import CategoryFactory, DiscountFactory

pytestmark = pytest.mark.django_db


class TestDiscountListAPIView:
    endpoint_url = "discount-list"

    def test_get_list(self, discounts, client: APIClient):
        response = client.get(reverse(self.endpoint_url))
        assert response.status_code == 200
        assert response.data["count"] == 5

    def test_get_list_only_active_discounts(
        self, discounts, inactive_discount: Discount, client: APIClient
    ):
        response = client.get(reverse(self.endpoint_url))
        assert response.status_code == 200
        assert response.data["count"] == 5
        assert Discount.objects.filter(
            id=inactive_discount.id, active=False
        ).exists()

    def test_get_list_only_started_discounts(
        self,
        discounts,
        unstarted_discount: Discount,
        client: APIClient,
    ):
        response = client.get(reverse(self.endpoint_url))
        assert response.status_code == 200
        assert response.data["count"] == 5
        assert Discount.objects.filter(id=unstarted_discount.id).exists()

    def test_get_list_exclude_ended_discount(
        self,
        discounts,
        ended_discount: Discount,
        client: APIClient,
    ):
        response = client.get(reverse(self.endpoint_url))
        assert response.status_code == 200
        assert response.data["count"] == 5
        assert Discount.objects.filter(id=ended_discount.id).exists()

    def test_get_list_search_by_category(
        self,
        discounts,
        client: APIClient,
    ):
        category = CategoryFactory(type="test-type")
        DiscountFactory(category=category, active=True)
        response = client.get(
            reverse(self.endpoint_url), {"search": category.id}
        )
        assert response.status_code == 200
        assert response.data["count"] == 1
