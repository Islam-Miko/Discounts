from django.db.models import F
from huey.contrib.djhuey import db_task

from .models import WatchedAmount


@db_task()
def increment_count(discount_id: int) -> None:
    """
    Huey task, increments WatchedAmount.amount.

    :params discount_id: id of related Discount
    :type discount_id: int
    """
    WatchedAmount.objects.filter(discount__id=discount_id).update(
        amount=F("amount") + 1
    )
