from datetime import timedelta

import pytest
from django.core.cache import cache
from django.utils import timezone
from rest_framework.test import APIClient

from authentication.models import DiscountUser

from .factories import (
    DiscountFactory,
    DiscountLimitFactory,
    DiscountUserFactory,
)


@pytest.fixture
def discounts():
    yield DiscountFactory.create_batch(5, active=True)


@pytest.fixture
def user() -> DiscountUser:
    return DiscountUserFactory()


@pytest.fixture
def base_client() -> APIClient:
    return APIClient()


@pytest.fixture(name="client")
def authenticated_client(
    base_client: APIClient, user: DiscountUser
) -> APIClient:
    base_client.force_authenticate(user)
    yield base_client
    base_client.logout()


@pytest.fixture
def inactive_discount():
    yield DiscountFactory(active=False)


@pytest.fixture
def unstarted_discount():
    yield DiscountFactory(
        start_date=timezone.now() + timedelta(days=1), active=True
    )


@pytest.fixture
def ended_discount():
    yield DiscountFactory(
        start_date=timezone.now() - timedelta(days=20), active=True
    )


@pytest.fixture
def one_discount(discounts):
    yield discounts[-1]


@pytest.fixture(autouse=True, scope="function")
def reset_cache():
    yield
    cache.clear()


@pytest.fixture(name="discount")
def discount_for_coupon():
    discount = DiscountFactory(active=True)
    DiscountLimitFactory(discount=discount, day_limit=1, total_limit=2)
    yield discount
