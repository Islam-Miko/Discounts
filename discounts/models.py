import uuid

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    """
    Base model with defined fields
    """

    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)


class Category(BaseModel):

    type = models.CharField("Category", max_length=100)
    order_num = models.IntegerField("Priority", default=0)

    def __str__(self):
        return f"{self.type}"


class City(BaseModel):

    city = models.CharField("City", max_length=100, unique=True)
    order_num = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return f"{self.city}"


class Description(BaseModel):

    description = models.TextField(verbose_name="Description")
    condition = models.TextField(verbose_name="Condition")
    days = models.TextField(verbose_name="Available days")
    active = models.BooleanField()
    work_hours = models.CharField("Work hours", max_length=255, null=True)
    discount = models.OneToOneField(
        "Discount",
        on_delete=models.CASCADE,
        related_name="description",
        null=True,
    )

    def __str__(self):
        return f"Description {self.pk}"


class Discount(BaseModel):

    percentage = models.PositiveSmallIntegerField("Discount percentage")
    start_date = models.DateTimeField("Start date")
    end_date = models.DateTimeField("End date")
    active = models.BooleanField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    company = models.ForeignKey("Company", on_delete=models.CASCADE)
    instruction = models.ForeignKey(
        "Instruction", on_delete=models.CASCADE, null=True
    )
    order_num = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return f"{self.percentage}%  {self.company.name} {self.city}"


class WatchedAmount(BaseModel):
    amount = models.PositiveIntegerField(verbose_name="Views", default=0)
    discount = models.OneToOneField(
        Discount,
        on_delete=models.CASCADE,
        null=True,
        unique=True,
        related_name="views",
    )

    def __str__(self):
        return f"{self.amount} {self.discount}"

    @receiver(post_save, sender=Discount)
    def create_watched_disc(sender, instance, created, **kwargs) -> None:
        if created:
            WatchedAmount.objects.create(discount=instance)


class Company(BaseModel):

    name = models.CharField(
        max_length=255, verbose_name="Company name", unique=True
    )
    image = models.ImageField(upload_to="media/company", verbose_name="Image")

    def __str__(self):
        return f"{self.name}"


class SocialNet(BaseModel):
    class SocialNetTypes(models.TextChoices):
        INSTAGRAM = "INSTAGRAM"
        FB = "FACEBOOK"
        TIKTOK = "TIKTOK"

    url = models.URLField(verbose_name="Link to account", null=True)
    type = models.CharField(
        choices=SocialNetTypes.choices,
        max_length=50,
        default=SocialNetTypes.INSTAGRAM,
        verbose_name="Type",
    )
    active = models.BooleanField(default=True)
    logo = models.ImageField(
        upload_to="media/social", null=True, verbose_name="Logo"
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, null=True, related_name="socials"
    )

    def __str__(self):
        return f"СС {self.type} {self.company}"


class Address(BaseModel):
    longitude = models.DecimalField(
        verbose_name="Longitude", max_digits=9, decimal_places=6
    )
    latitude = models.DecimalField(
        verbose_name="Latitude", max_digits=9, decimal_places=7
    )
    street = models.CharField("Street", max_length=255)
    house = models.PositiveIntegerField("House")
    city = models.ForeignKey(
        City, on_delete=models.CASCADE, verbose_name="City"
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, null=True, related_name="addresses"
    )

    def __str__(self):
        return f"{self.company} {self.city}, {self.street} {self.house}"


class Number(BaseModel):
    phone = models.CharField("Phone number", max_length=25, unique=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, null=True, related_name="phones"
    )

    def __str__(self):
        return f"{self.company} {self.phone}"


class ClientDetail(BaseModel):
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    city = models.ForeignKey(City, on_delete=models.CASCADE)


class ClientDiscount(BaseModel):
    class STATUSES(models.TextChoices):
        BOOKED = "BOOKED", _("BOOKED")
        WASTED = "WASTED", _("WASTED")
        ACTIVATED = "ACTIVATED", _("ACTIVATED")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    add_date = models.DateTimeField(auto_now_add=True)
    edit_date = models.DateTimeField(auto_now=True)
    status = models.CharField(
        choices=STATUSES.choices,
        max_length=50,
        default=STATUSES.BOOKED,
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.client.phone_number} - {self.status} {self.edit_date}"


class DiscountLimit(BaseModel):
    day_limit = models.PositiveSmallIntegerField(verbose_name="Day limit")
    total_limit = models.PositiveSmallIntegerField(
        verbose_name="Total coupons"
    )
    discount = models.ForeignKey(
        Discount, on_delete=models.CASCADE, related_name="limits"
    )

    def __str__(self):
        return f"Limits {self.discount}"


class Review(BaseModel):
    text = models.TextField()
    add_date = models.DateTimeField(auto_now_add=True)
    author = models.CharField("Author", max_length=25)
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.author} {self.discount}"


class Instruction(BaseModel):
    text = models.TextField()

    def __str__(self):
        return self.text
