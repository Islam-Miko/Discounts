from datetime import timedelta

from django.db.models import F
from django.utils import timezone
from huey import crontab
from huey.contrib.djhuey import db_periodic_task, db_task

from .models import ClientDiscount, WatchedAmount


@db_task()
def increment_count(discount_id: int) -> None:
    """
    Huey task, increments WatchedAmount.amount.

    :params discount_id: id of related Discount
    :type discount_id: int
    """
    WatchedAmount.objects.filter(
        discount__id=discount_id, discount__active=True
    ).update(amount=F("amount") + 1)


@db_periodic_task(crontab())
def coupon_checker() -> None:
    """
    Huey db_task, checks for wasted ClientDiscounts (Coupons) and if there are some
    updates status from 'BOOKED' to 'WASTED'
    """
    ClientDiscount.objects.filter(
        add_date__lt=timezone.now() - timedelta(days=2),
        status=ClientDiscount.STATUSES.BOOKED,
    ).update(status=ClientDiscount.STATUSES.WASTED)
