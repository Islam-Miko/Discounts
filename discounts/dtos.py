import datetime

from . import models


class discountDtoWhole:
    """Для полного вывода инвы про акцию"""
    def __init__(self, discount):
        self.id = discount.id
        self.description = discount.description.description
        self.days = discount.description.days
        self.condition = discount.description.condition
        self.work_hours = discount.description.work_hours
        self.company = discount.company.name
        self.address = models.Address.objects.filter(company=discount.company).last()
        self.socials = models.SocialNet.objects.filter(company=discount.company)
        self.phones = discount.company.phones
        self.views = discount.views
        self.instruction = discount.instruction.text
        self.percentage = discount.percentage
        self.image = discount.company.image
        # self.order_num = discount.order_num


class couponDto:
    """Для получения купона"""
    format = '%d.%m.%Y %H:%M:%S'
    today = datetime.datetime.today()
    today += datetime.timedelta(days=2)

    todayy = datetime.datetime.today()
    day_48_hours_ago = todayy - datetime.timedelta(days=2)

    def __init__(self, discount, client):
        self.duration_time = models.ClientDiscount.objects.filter(add_date__gte=self.day_48_hours_ago,
                                                                  status='BOOKED')\
            .get(discount=discount, client=client).add_date + datetime.timedelta(days=2)
        self.company = models.Company.objects.filter(discount=discount).get().name
        self.logo = models.Company.objects.filter(discount=discount).get().image
        self.description= discount.description.description
        self.percentage = discount.percentage
        self.time_limit = f'Купон действует до {self.duration_time}'[0:38]



class discountDtoShort:
    """Для краткой информации об акциях"""
    def __init__(self, discount):
        self.id = discount.id
        self.description = models.Description.objects.filter(discount=discount).get().description
        self.days = discount.description.days
        self.company = discount.company
        self.city = models.Address.objects.filter(company=self.company).get().city
        self.views = models.WatchedAmount.objects.filter(discount=discount).get().amount
        self.percentage = discount.percentage
        # self.city_order = models.Address.objects.filter(company=self.company).get().city.order_num
        # self.order_num = discount.order_num

