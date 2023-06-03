from django.utils import timezone
from rest_framework import serializers

from . import models


class AddressSerializer(serializers.ModelSerializer):
    """AddressSerializer"""

    city = serializers.SlugRelatedField(
        slug_field="city", queryset=models.City.objects.all()
    )

    class Meta:
        model = models.Address
        exclude = ("id", "company")


class SocialSerializer(serializers.ModelSerializer):
    """SocialSerializer"""

    class Meta:
        model = models.SocialNet
        exclude = ("id", "active", "company")


class PhoneSerializer(serializers.ModelSerializer):
    """PhoneSerializer"""

    class Meta:
        model = models.Number
        exclude = ("id", "company")


class CompanySerializer2(serializers.ModelSerializer):
    """CompanySerializer2"""

    class Meta:
        model = models.Company
        fields = (
            "name",
            "image",
        )


class ReviewSerializer(serializers.ModelSerializer):
    """ReviewSerializer"""

    class Meta:
        model = models.Review
        fields = "__all__"


class CouponGetSerializer(serializers.Serializer):
    """
    CouponGetSerializer.
    Used in coupon creation endpoint
    """

    id = serializers.UUIDField(read_only=True)
    titel = serializers.CharField(default="DISCOUNT COUPON", required=False)
    company = serializers.CharField()
    percentage = serializers.IntegerField()
    description = serializers.CharField()
    valid_time = serializers.SerializerMethodField()
    image = serializers.SlugField()

    def get_valid_time(self, obj) -> str:
        return f"Coupon is valid until {timezone.localtime(obj.valid_time): %d.%m.%Y %H:%M}"


class DiscountSerializer(serializers.ModelSerializer):
    order_num = serializers.IntegerField(write_only=True)

    class Meta:
        model = models.Discount
        fields = "__all__"


class DiscountShortInformationSerializer(DiscountSerializer):
    """
    DiscountShortInformationSerializer.
    Used in list-view endpoint to output short information about Discount
    """

    category = serializers.CharField(source="category.type")
    company = serializers.CharField(source="company.name")
    instruction = serializers.CharField(source="instruction.text")


class CompanyFullInformationSerializer(CompanySerializer2):
    """CompanyFullInformationSerializer"""

    class Meta(CompanySerializer2.Meta):
        fields = "__all__"


class DescriptionSerializer(serializers.ModelSerializer):
    """DescriptionSerializer"""

    class Meta:
        model = models.Description
        fields = "__all__"


class DiscountFullInformationSerializer(DiscountShortInformationSerializer):
    """
    DiscountFullInformationSerializer.
    Used in detail-view endpoint to output full information about Discount
    """

    views_count = serializers.IntegerField()
    company = CompanyFullInformationSerializer()
    description = DescriptionSerializer()
    company_socials = serializers.ListSerializer(child=serializers.DictField())
    company_phones = serializers.ListField(child=serializers.CharField())
    addres = serializers.CharField()
    discount_city = serializers.CharField()


class CouponCreateSerializer(serializers.ModelSerializer):
    """
    CouponCreateSerializer.
    Used in to create coupon (ClientDiscount) for client.
    """

    id = serializers.UUIDField(read_only=True)
    discount = serializers.PrimaryKeyRelatedField(
        queryset=models.Discount.objects.all()
    )

    class Meta:
        model = models.ClientDiscount
        fields = ("client", "discount", "id")


class SuccessfulResponseSerializer(serializers.Serializer):
    """SuccessfulResponseSerializer.
    Used to show response body schema in swagger"""

    message = serializers.CharField(default="Ok")
