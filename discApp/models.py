from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from .validation_func import (check_lte_100,
                              check_is_numeric)


class Category(models.Model):
    """Категория акций"""
    type = models.CharField('Категория', max_length=100)

    def __str__(self):
        return f'{self.type}'


class City(models.Model):
    """Города"""
    CITIES = (
        ('osh', 'Ош'),
        ('bishkek', 'Бишкек')
    )
    city = models.CharField('Город', max_length=100,
                            choices=CITIES)

    def __str__(self):
        return f'{self.city}'


class Description(models.Model):
    """Описание акции с условиями"""
    description = models.TextField(verbose_name='Описание')
    condition = models.TextField(verbose_name='Условине')
    days = models.TextField(verbose_name='Дни использования')
    active = models.BooleanField()

    def __str__(self):
        return f'Описание {self.pk}'


class Discount(models.Model):
    """Акция"""
    percentage = models.PositiveSmallIntegerField('Процент скидки', validators=[check_lte_100,])
    start_date = models.DateTimeField('Начало акции')
    end_date = models.DateTimeField('Окончание акции')
    pincode = models.CharField(max_length=20, validators=[check_is_numeric,])
    active = models.BooleanField()
    description = models.ForeignKey(Description, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    company = models.ForeignKey('Company', on_delete=models.CASCADE)
    instruction = models.ForeignKey('Instruction', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.percentage}%  {self.company.name} {self.city}'

    def increment(self):
        WatchedAmount.objects.filter(discount=self).last().increment()

    @property
    def views(self):
        return WatchedAmount.objects.filter(discount=self).get().amount

    @property
    def city(self):
        return self.company.city


class WatchedAmount(models.Model):
    """Счетчик просмотров акций в приложении"""
    amount = models.PositiveIntegerField(verbose_name='Количество просмотров',
                                         default=0)
    discount = models.OneToOneField(Discount, on_delete=models.CASCADE, null=True,
                                 unique=True)

    def increment(self):
        self.amount += 1
        self.save()

    def __str__(self):
        return f'{self.amount} {self.discount}'

    @receiver(post_save, sender=Discount)  # add this
    def create_watched_disc(sender, instance, created, **kwargs):
        if created:
            WatchedAmount.objects.create(discount=instance)


class Company(models.Model):
    """Филиалы главной компании"""
    name = models.CharField(max_length=255, verbose_name='Компания')
    image = models.ImageField(upload_to='media/company')

    def __str__(self):
        return f'{self.name}'

    @property
    def city(self):
        return Address.objects.get(company=self).city


class SocialNet(models.Model):
    """Социальные сети компании"""
    INSTA = 'INSTA'
    FB = 'FB'
    VK = 'VK'
    TIKTOK = 'TIKTOK'
    TYPE = (
        (INSTA, 'Инстаграм'),
        (FB, 'FaceBook'),
        (VK, 'ВКонтакте'),
        (TIKTOK, 'TIKTOK'),
    )
    url = models.URLField(verbose_name='Ссылка на аккаунт', null=True)
    type = models.CharField(choices=TYPE, max_length=50, default=VK)
    active = models.BooleanField(default=True)
    logo = models.ImageField(upload_to='media/social', null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True,
                                related_name='socials')

    def __str__(self):
        return f'СС {self.type} {self.company}'


class Address(models.Model):
    """Адрес"""
    longitude = models.DecimalField(verbose_name='Долгота', max_digits=9, decimal_places=6)
    latitude = models.DecimalField(verbose_name='Широта', max_digits=9, decimal_places=7)
    street = models.CharField('Улица', max_length=255)
    house = models.PositiveIntegerField('Дом')
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True,
                                related_name='addresses')

    def __str__(self):
        return f'{self.company} {self.city}, {self.street} {self.house}'


class Number(models.Model):
    """Телефонный номер"""
    phone = models.CharField('Номер телефона', max_length=25, unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True,
                                related_name='phones')

    def __str__(self):
        return f'{self.company} {self.phone}'


class Client(models.Model):
    """Пользователь-клиент"""
    phone = models.CharField('номер телефона', max_length=25, unique=True)
    passport = models.CharField('ИНН', max_length=25, unique=True, null=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.phone}'


class ClientDiscount(models.Model):
    """История использований акций(купонов)"""
    STATUS = (
        ('BOOKED', 'Забронирован'),
        ('ACTIVATED', 'Активирован')
    )
    add_date = models.DateTimeField(auto_now_add=True)
    edit_date = models.DateTimeField(auto_now=True)
    status = models.CharField(choices=STATUS, max_length=50)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.client.phone} - {self.status} {self.edit_date}'


class DiscountLimit(models.Model):
    """Ограничения для акции"""
    day_limit = models.PositiveSmallIntegerField(verbose_name='Ограничение на 1 день')
    total_limit = models.PositiveSmallIntegerField(verbose_name='Количество купонов')
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE)

    def __str__(self):
        return f' Лимиты {self.discount}'


class Review(models.Model):
    """Отзыв"""
    text = models.TextField()
    add_date = models.DateTimeField(auto_now_add=True)
    author = models.CharField('Автор', max_length=25)
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.author} на {self.discount}'


class Instruction(models.Model):
    text = models.TextField()

    def __str__(self):
        return 'Инструкция'


