from django.core.exceptions import ValidationError


def check_lte_100(number):
    if number > 100:
        raise ValidationError('Percentage cannot be greater than 100%')


def check_is_numeric(number):
    if not number.isnumeric():
        raise ValidationError('Pincode should consist only digits')