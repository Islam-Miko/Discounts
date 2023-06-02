import datetime

from django.db.models import DateTimeField, ExpressionWrapper, F
from django.utils import timezone

from authentication.models import DiscountUser

from . import models
from .exceptions import (
    AlreadyHaveCoupon,
    DayLimitIsReached,
    DiscountIsNotActive,
)
from .models import ClientDiscount, Discount, DiscountLimit


def check_conditions(discount_id: int, client: DiscountUser) -> None:
    today = timezone.now()
    discount_limit: DiscountLimit = DiscountLimit.objects.get(
        discount__id=discount_id
    )

    if ClientDiscount.objects.filter(
        discount__id=discount_id,
        client=client,
        status=ClientDiscount.STATUSES.BOOKED,
    ).exists():
        raise AlreadyHaveCoupon()

    client_discount_base = ClientDiscount.objects.filter(
        discount__id=discount_id
    )

    day_use_of_discount = client_discount_base.filter(
        add_date__date=today.date()
    ).count()

    total_uses_of_discount = client_discount_base.filter(
        status=ClientDiscount.STATUSES.ACTIVATED
    ).count()

    if total_uses_of_discount >= discount_limit.total_limit:
        Discount.objects.filter(id=discount_id).update(active=False)
        raise DiscountIsNotActive()
    elif day_use_of_discount >= discount_limit.day_limit:
        raise DayLimitIsReached()


def get_object_by_id(queryset, id: int) -> object:
    """Селектор для получения экземпляра по id из заданной модели"""
    return queryset.objects.filter(id=id).get()


def find_last_BOOKED_object_of_client(
    discount: object, client: object
) -> object:
    """При активации акции, меняем стаутс последней записи - возвращает посл.запись"""
    return models.ClientDiscount.objects.filter(
        discount=discount, client=client, status="BOOKED"
    ).last()


def couponScheduler() -> None:
    """Для бэкграунд чека - прошло ли время действия купона"""
    for_checking_querysets = models.ClientDiscount.objects.filter(
        status="BOOKED"
    ).all()
    hours_48 = datetime.timedelta(minutes=1)
    today = datetime.datetime.today()
    for check_obj in for_checking_querysets:
        if str(check_obj.add_date + hours_48) <= str(today):
            check_obj.status = models.ClientDiscount.STATUS[1][0]
            check_obj.save()


def get_coupon(coupon_id: int) -> ClientDiscount:
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
