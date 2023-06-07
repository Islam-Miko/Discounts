from unittest.mock import patch

import pytest
from django.contrib.postgres.aggregates import ArrayAgg
from django.db import models as m
from django.db.models.functions import Concat, JSONObject
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from discounts.models import Discount
from discounts.serializers import DiscountFullInformationSerializer

from .factories import DiscountFactory

pytestmark = pytest.mark.django_db


class TestDiscountDetailAPIView:
    endpoint_url = "discount-detail"

    def test_get_discount(self, client: APIClient):
        discount = DiscountFactory(active=True)
        url = reverse(self.endpoint_url, kwargs={"pk": discount.id})

        with patch("discounts.decorators.increment_count") as mocked_task:
            response = client.get(url)
            mocked_task.assert_called_once_with(discount.id)

        assert response.status_code == status.HTTP_200_OK

    def test_not_found(self, client: APIClient):
        discount = DiscountFactory(active=False)
        url = reverse(self.endpoint_url, kwargs={"pk": discount.id})

        with patch("discounts.decorators.increment_count") as mocked_task:
            response = client.get(url)
            mocked_task.assert_called_once_with(discount.id)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_discount_fields(self, client: APIClient):
        discount = DiscountFactory(active=True)
        url = reverse(self.endpoint_url, kwargs={"pk": discount.id})
        instance = (
            Discount.objects.filter(active=True)
            .select_related(
                "description", "views", "company", "instruction", "category"
            )
            .annotate(
                views_count=m.F("views__amount"),
                discount_city=m.F("company__addresses__city__city"),
                addres=Concat(
                    m.F("company__addresses__street"),
                    m.Value(" "),
                    m.F("company__addresses__house"),
                    output_field=m.CharField(),
                ),
                company_phones=ArrayAgg(m.F("company__phones__phone")),
                company_socials=ArrayAgg(
                    JSONObject(
                        url=m.F("company__socials__url"),
                        type=m.F("company__socials__type"),
                        logo=m.F("company__socials__logo"),
                    )
                ),
            )
            .get(id=discount.id)
        )
        test_serializer = DiscountFullInformationSerializer(instance)

        with patch("discounts.decorators.increment_count") as mocked_task:
            response = client.get(url)
            mocked_task.assert_called_once_with(discount.id)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == test_serializer.data
