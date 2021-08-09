import datetime
import itertools
from rest_framework import filters
from collections import deque
from rest_framework.settings import api_settings
from . import models
from . import dtos


class ByCityFilterBackend(filters.BaseFilterBackend):
    """Кастомный фильтр по городам"""
    search_param = api_settings.SEARCH_PARAM

    def get_search_terms(self, request):
        """
        Search terms are set by a ?search=... query parameter,
        and may be comma and/or whitespace delimited.
        """
        params = request.query_params.get('city', '')
        params = params.replace('\x00', '')  # strip null characters
        params = params.replace(',', ' ')
        return params

    def filter_queryset(self, request, queryset, view):
        search_terms = self.get_search_terms(request)
        print(search_terms)
        if not search_terms:
            return queryset
        needed_cities = filter(lambda x: x.company.city.id == int(search_terms), queryset)
        rest_cities = filter(lambda x: x.company.city.id != int(search_terms), queryset)

        return itertools.chain(needed_cities, rest_cities)


def coupon_creation(discount, client):
    today = datetime.datetime.today()
    day_48_hours_ago = today - datetime.timedelta(days=2)
    # day_48_hours_ago нужен, чтобы найти созданный в течение последних 2 суток объект со
    # статусом BOOKED

    day_use_of_discount = models.ClientDiscount.objects.filter(add_date__day=today.day,
                                                               discount=discount).count()
    # Запрос возвращает количество полученных(или использованных) сегодня купонов у заданной акции
    total_uses_of_discount = models.ClientDiscount.objects.filter(status='ACTIVATED',
                                                                  discount=discount).count()
    # Запрос возвращает сколько раз акция была применена клиентом
    day_limit = models.DiscountLimit.objects.filter(discount=discount).get().day_limit
    total_limit = models.DiscountLimit.objects.filter(discount=discount).get().total_limit
    # Запросы возвращают лимиты заданные для акции

    clients_last_coupon = models.ClientDiscount.objects.filter(discount=discount,
                                                               client=client).last()
    # Запрос возвращает последний купон клиента на заданную акцию
    if clients_last_coupon:
        if clients_last_coupon.status == 'BOOKED':
            return False, '_'
    # Если у клиента есть купон и он ее еще не воспользовался, то на экране выйдет его купон

    if total_uses_of_discount >= total_limit:
        return True, 'No more Coupons.'
    elif day_use_of_discount >= day_limit:
        return True, 'No more Coupons for today, Im sorry!'
    # Если условия ограничений количества использований акции превышены, то нельзя получить новый купон.

    models.ClientDiscount.objects.filter(add_date__gte=day_48_hours_ago).get_or_create(discount=discount,
                                                                                       client=client,
                                                                                       status='BOOKED')
# При первичном запросе создает запись в модели,
#     ищет по дате за последнии 2 дня, так как купон дается на 2 дня
    return False, ' '


def make_list_dto(queryset):
    """для вывода списка объектов через дто"""
    a_list = []
    for query in queryset:
        a_list.append(dtos.discountDtoShort(query))
    return a_list


def get_object_by_id(queryset, id):
    """Селектор для получения экземпляра по id из заданной модели"""
    return queryset.objects.filter(id=id).get()


def find_last_BOOKED_object_of_client(discount, client):
    """При активации акции, меняем стаутс последней записи - возвращает посл.запись"""
    return models.ClientDiscount.objects.filter(discount=discount,
                                                client=client, status='BOOKED').last()


def couponScheduler():
    """Для бэкграунд чека - прошло ли время действия купона"""
    for_checking_querysets = models.ClientDiscount.objects.filter(status='BOOKED').all()
    hours_48 = datetime.timedelta(minutes=1)
    today = datetime.datetime.today()
    for check_obj in for_checking_querysets:
        if str(check_obj.add_date + hours_48) <= str(today):
            check_obj.status = models.ClientDiscount.STATUS[1][0]
            check_obj.save()




