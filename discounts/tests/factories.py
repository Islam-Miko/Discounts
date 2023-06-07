from datetime import timedelta
from random import randint

import factory
from django.utils import timezone
from factory import fuzzy
from factory.faker import Faker

from authentication import models as auth_model
from discounts import models


class DiscountUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = auth_model.DiscountUser

    username = factory.Faker("user_name")
    email = factory.Faker("email")
    phone_number = factory.Faker("numerify", text="############")
    passport_id = factory.Faker("numerify", text="############")


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Category


class CompanyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Company

    name = factory.Sequence(lambda x: f"Company {x}")


class InstructionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Instruction


class DiscountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Discount

    percentage = fuzzy.FuzzyInteger(1, 100)
    start_date = Faker(
        "date_time_between",
        start_date="-1w",
        end_date="now",
        tzinfo=timezone.get_current_timezone(),
    )
    end_date = factory.LazyAttribute(
        lambda obj: obj.start_date + timedelta(days=7)
    )
    active = fuzzy.FuzzyChoice([True, False])
    category = factory.SubFactory(CategoryFactory)
    company = factory.SubFactory(CompanyFactory)
    instruction = factory.SubFactory(InstructionFactory)
    order_num = factory.Sequence(lambda n: n + 1)


class DiscountLimitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.DiscountLimit

    day_limit = randint(1, 10)
    total_limit = randint(10, 50)


class ClientDiscountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ClientDiscount

    client = factory.SubFactory(DiscountUserFactory)
    discount = factory.SubFactory(DiscountFactory)
