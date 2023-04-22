import datetime

from . import models


class couponDto:
    """Для получения купона"""

    format = "%d.%m.%Y %H:%M:%S"
    today = datetime.datetime.today()
    today += datetime.timedelta(days=2)

    todayy = datetime.datetime.today()
    day_48_hours_ago = todayy - datetime.timedelta(days=2)

    def __init__(self, discount, client):
        self.duration_time = models.ClientDiscount.objects.filter(
            add_date__gte=self.day_48_hours_ago, status="BOOKED"
        ).get(discount=discount, client=client).add_date + datetime.timedelta(
            days=2
        )
        self.company = (
            models.Company.objects.filter(discount=discount).get().name
        )
        self.logo = (
            models.Company.objects.filter(discount=discount).get().image
        )
        self.description = discount.description.description
        self.percentage = discount.percentage
        self.time_limit = f"Купон действует до {self.duration_time}"[0:38]
