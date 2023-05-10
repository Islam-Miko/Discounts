from django.contrib.auth.models import AbstractUser
from django.db import models


class DiscountUser(AbstractUser):
    phone_number = models.CharField(max_length=12, unique=True, null=False)
    passport_id = models.CharField(max_length=25, unique=True, null=False)

    REQUIRED_FIELDS = ["passport_id", "phone_number"]
