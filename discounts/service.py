import datetime

from django.db.models import DateTimeField, ExpressionWrapper, F
from django.utils import timezone

from authentication.models import DiscountUser

from .exceptions import (
    AlreadyHaveCoupon,
    DayLimitIsReached,
    DiscountIsNotActive,
)
from .models import ClientDiscount, Discount, DiscountLimit


def check_conditions(discount_id: int, client: DiscountUser) -> None:
    """
    Func to check conditions before creation of ClientDiscount.
    Conditions:
        1) If the client already has a coupon.
        2) If the total discount limit has been reached (enough coupons have been activated).
        3) If the daily limit of created coupons has been reached.
    If any condition matches raises appropriate Exception

    :params discount_id: id of Discount
    :type discount_id: int
    :params client: Client (User) instance
    :type client: DiscountUser
    :return: -
    :rtype: None
    """
    today = timezone.now()
    discount_limit: DiscountLimit = DiscountLimit.objects.get(
        discount__id=discount_id
    )

    # check for condition (1)
    if ClientDiscount.objects.filter(
        discount__id=discount_id,
        client=client,
        status=ClientDiscount.STATUSES.BOOKED,
    ).exists():
        raise AlreadyHaveCoupon()

    # base queryset to not double code
    client_discount_base = ClientDiscount.objects.filter(
        discount__id=discount_id
    )

    day_use_of_discount = client_discount_base.filter(
        add_date__date=today.date()
    ).count()

    total_uses_of_discount = client_discount_base.filter(
        status=ClientDiscount.STATUSES.ACTIVATED
    ).count()
    # check for condition (2)
    if total_uses_of_discount >= discount_limit.total_limit:
        Discount.objects.filter(id=discount_id).update(active=False)
        raise DiscountIsNotActive()
    # check for condition (3)
    elif day_use_of_discount >= discount_limit.day_limit:
        raise DayLimitIsReached()


def get_coupon(coupon_id: str) -> ClientDiscount:
    """
    Func to get ClientDiscount with annotated fields.

    :params coupon_id: id of ClientDiscount
    :type coupon_id: int
    :return: Coupon (ClientDiscount)
    :rtype: ClientDiscount
    """
    return ClientDiscount.objects.annotate(
        company=F("discount__company__name"),
        image=F("discount__company__image"),
        description=F("discount__description__description"),
        percentage=F("discount__percentage"),
        valid_time=ExpressionWrapper(
            F("add_date") + datetime.timedelta(days=2),
            output_field=DateTimeField(),
        ),
    ).get(id=coupon_id)


def activate_coupon(coupon_id: str) -> None:
    """
    Func to update ClientDiscount status to 'ACTIVATED'

    :params coupon_id: id of ClientDiscount
    :type coupon_id: int
    :return: -
    :rtype: None
    """
    ClientDiscount.objects.filter(id=coupon_id).update(
        status=ClientDiscount.STATUSES.ACTIVATED
    )
