from rest_framework import serializers

from . import models, validators


class AddressSerializer(serializers.ModelSerializer):
    """Для полной информации"""

    city = serializers.SlugRelatedField(
        slug_field="city", queryset=models.City.objects.all()
    )

    class Meta:
        model = models.Address
        exclude = ("id", "company")


class SocialSerializer(serializers.ModelSerializer):
    """Для полной информации"""

    class Meta:
        model = models.SocialNet
        exclude = ("id", "active", "company")


class PhoneSerializer(serializers.ModelSerializer):
    """Для полной информации"""

    class Meta:
        model = models.Number
        exclude = ("id", "company")


class CompanySerializer2(serializers.ModelSerializer):
    """Для краткой информацииж об компании"""

    class Meta:
        model = models.Company
        fields = (
            "name",
            "image",
        )


class ReviewSerializer(serializers.ModelSerializer):
    """Для краткой информацииж об компании"""

    class Meta:
        model = models.Review
        fields = "__all__"


class CouponSerializer(serializers.Serializer):

    titel = serializers.CharField(default="СКИДОЧНЫЙ КУПОН", required=False)
    company = serializers.CharField()
    percentage = serializers.IntegerField()
    description = serializers.CharField()
    time_limit = serializers.CharField()
    logo = serializers.SlugField()


class PincodeValidationSerialzier(serializers.Serializer):
    pincode = serializers.CharField(
        min_length=4,
        max_length=4,
        validators=[
            validators.check_is_numeric,
        ],
    )


class CategorySerialzir(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = "__all__"


class DiscountSerializer(serializers.ModelSerializer):
    pincode = serializers.CharField(write_only=True)
    order_num = serializers.IntegerField(write_only=True)

    class Meta:
        model = models.Discount
        fields = "__all__"


class DiscountShortInformationSerializer(DiscountSerializer):
    category = serializers.CharField(source="category.type")
    company = serializers.CharField(source="company.name")
    instruction = serializers.CharField(source="instruction.text")


class CompanyFullInformationSerializer(CompanySerializer2):
    class Meta(CompanySerializer2.Meta):
        fields = "__all__"


class InstuctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Instruction
        fields = "__all__"


class DescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Description
        fields = "__all__"


class DiscountFullInformationSerializer(DiscountShortInformationSerializer):
    views_count = serializers.IntegerField()
    company = CompanyFullInformationSerializer()
    description = DescriptionSerializer()
    company_socials = serializers.ListSerializer(child=serializers.DictField())
    company_phones = serializers.ListField(child=serializers.CharField())
    addres = serializers.CharField()
    discount_city = serializers.CharField()
