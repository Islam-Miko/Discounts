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
    """Категория акций"""

    type = models.CharField("Категория", max_length=100)
    order_num = models.IntegerField("Приоритет", default=0)

    def __str__(self):
        return f"{self.type}"


class City(BaseModel):
    """Города"""

    city = models.CharField("Город", max_length=100, unique=True)
    order_num = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return f"{self.city}"


class Description(BaseModel):
    """Описание акции с условиями"""

    description = models.TextField(verbose_name="Описание")
    condition = models.TextField(verbose_name="Условине")
    days = models.TextField(verbose_name="Дни использования")
    active = models.BooleanField()
    work_hours = models.CharField("Время работы", max_length=255, null=True)
    discount = models.OneToOneField(
        "Discount",
        on_delete=models.CASCADE,
        related_name="description",
        null=True,
    )

    def __str__(self):
        return f"Описание {self.pk}"


class Discount(BaseModel):
    """Акция"""

    percentage = models.PositiveSmallIntegerField("Процент скидки")
    start_date = models.DateTimeField("Начало акции")
    end_date = models.DateTimeField("Окончание акции")
    pincode = models.CharField(max_length=20)
    active = models.BooleanField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    company = models.ForeignKey("Company", on_delete=models.CASCADE)
    instruction = models.ForeignKey(
        "Instruction", on_delete=models.CASCADE, null=True
    )
    order_num = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return f"{self.percentage}%  {self.company.name} {self.city}"

    def increment(self):
        WatchedAmount.objects.filter(discount=self).last().increment()

    @property
    def city(self):
        return self.company.city

    @property
    def city_order(self) -> int:
        return self.company.city.order_num


class WatchedAmount(BaseModel):
    """Счетчик просмотров акций в приложении"""

    amount = models.PositiveIntegerField(
        verbose_name="Количество просмотров", default=0
    )
    discount = models.OneToOneField(
        Discount,
        on_delete=models.CASCADE,
        null=True,
        unique=True,
        related_name="views",
    )

    def increment(self) -> None:
        self.amount += 1
        self.save()

    def __str__(self):
        return f"{self.amount} {self.discount}"

    @receiver(post_save, sender=Discount)  # add this
    def create_watched_disc(sender, instance, created, **kwargs) -> None:
        if created:
            WatchedAmount.objects.create(discount=instance)


class Company(BaseModel):
    """Филиалы главной компании"""

    name = models.CharField(
        max_length=255, verbose_name="Компания", unique=True
    )
    image = models.ImageField(
        upload_to="media/company", verbose_name="Картинка"
    )

    def __str__(self):
        return f"{self.name}"

    @property
    def city(self):
        return Address.objects.get(company=self).city


class SocialNet(BaseModel):
    """Социальные сети компании"""

    class SocialNetTypes(models.TextChoices):
        INSTAGRAM = "Instagram"
        FB = "Facebook"
        TIKTOK = "TIKTOK"

    url = models.URLField(verbose_name="Ссылка на аккаунт", null=True)
    type = models.CharField(
        choices=SocialNetTypes.choices,
        max_length=50,
        default=SocialNetTypes.INSTAGRAM,
        verbose_name="Тип",
    )
    active = models.BooleanField(default=True)
    logo = models.ImageField(
        upload_to="media/social", null=True, verbose_name="Лого"
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, null=True, related_name="socials"
    )

    def __str__(self):
        return f"СС {self.type} {self.company}"


class Address(BaseModel):
    """Адрес"""

    longitude = models.DecimalField(
        verbose_name="Долгота", max_digits=9, decimal_places=6
    )
    latitude = models.DecimalField(
        verbose_name="Широта", max_digits=9, decimal_places=7
    )
    street = models.CharField("Улица", max_length=255)
    house = models.PositiveIntegerField("Дом")
    city = models.ForeignKey(
        City, on_delete=models.CASCADE, verbose_name="Город"
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, null=True, related_name="addresses"
    )

    def __str__(self):
        return f"{self.company} {self.city}, {self.street} {self.house}"


class Number(BaseModel):
    """Телефонный номер"""

    phone = models.CharField("Номер телефона", max_length=25, unique=True)
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
    """История использований акций(купонов)"""

    class STATUSES(models.TextChoices):
        BOOKED = "BOOKED", _("BOOKED")
        WASTED = "WASTED", _("WASTED")
        ACTIVATED = "ACTIVATED", _("ACTIVATED")

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
        return f"{self.client.phone} - {self.status} {self.edit_date}"


class DiscountLimit(BaseModel):
    """Ограничения для акции"""

    day_limit = models.PositiveSmallIntegerField(
        verbose_name="Ограничение на 1 день"
    )
    total_limit = models.PositiveSmallIntegerField(
        verbose_name="Количество купонов"
    )
    discount = models.ForeignKey(
        Discount, on_delete=models.CASCADE, related_name="limits"
    )

    def __str__(self):
        return f" Лимиты {self.discount}"


class Review(BaseModel):
    """Отзыв"""

    text = models.TextField()
    add_date = models.DateTimeField(auto_now_add=True)
    author = models.CharField("Автор", max_length=25)
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.author} на {self.discount}"


class Instruction(BaseModel):
    text = models.TextField()

    def __str__(self):
        return "Инструкция"
