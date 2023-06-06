from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from authentication.models import DiscountUser

from .factories import DiscountFactory, DiscountUserFactory


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
