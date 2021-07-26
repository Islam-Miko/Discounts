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
    company = models.ForeignKey('CompanyBranch', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.percentage}%  {self.company.main_company.name}'

    def increment(self):
        WatchedAmount.objects.filter(discount=self).last().increment()


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


class CompanyBranch(models.Model):
    """Филиалы главной компании"""
    image = models.ImageField(upload_to='media/company')
    main_company = models.ForeignKey('MainCompany', on_delete=models.CASCADE)
    address = models.ForeignKey('Address', on_delete=models.CASCADE)
    phone_number = models.ForeignKey('Number', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.main_company.name} {self.address}'


class MainCompany(models.Model):
    """Главная компания"""
    name = models.CharField(max_length=255, verbose_name='Компания')
    social_net = models.ForeignKey('SocialNet', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name}'


class SocialNet(models.Model):
    """Социальные сети компании"""
    instagram = models.CharField('Instagram', max_length=255)
    facebook = models.CharField('FaceBook', max_length=255)
    youtube = models.CharField('YouTube', max_length=255)
    telegram = models.CharField('Telegram', max_length=255)
    tiktok = models.CharField('TikTok', max_length=255)

    def __str__(self):
        return f'СС {self.pk}'


class Address(models.Model):
    """Адрес"""
    longitude = models.DecimalField(verbose_name='Долгота', max_digits=9, decimal_places=6)
    latitude = models.DecimalField(verbose_name='Широта', max_digits=9, decimal_places=7)
    street = models.CharField('Улица', max_length=255)
    house = models.PositiveIntegerField('Дом')
    city = models.ForeignKey(City, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.city}, {self.street} {self.house}'

class Number(models.Model):
    """Телефонный номер"""
    phone = models.CharField('Номер телефона', max_length=25)

    def __str__(self):
        return f'{self.phone}'


class Client(models.Model):
    """Пользователь-клиент"""
    phone = models.CharField('номер телефона', max_length=25)
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
    author = models.ForeignKey(Client, on_delete=models.CASCADE)
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.author} на {self.discount}'


