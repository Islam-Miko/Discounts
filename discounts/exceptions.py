from rest_framework import status
from rest_framework.exceptions import APIException


class AlreadyHaveCoupon(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Already have a coupon!"


class DayLimitIsReached(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Day limit is reached!"


class DiscountIsNotActive(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Discounts coupon is runned out!"
