from rest_framework import serializers
from . import models, validation_func


class AddressSerializer(serializers.ModelSerializer):
    """Для полной информации"""
    city = serializers.SlugRelatedField(slug_field='city', queryset=models.City.objects.all())

    class Meta:
        model = models.Address
        exclude = (
            'id',
            'company'
        )


class SocialSerializer(serializers.ModelSerializer):
    """Для полной информации"""
    class Meta:
        model = models.SocialNet
        exclude = (
            'id',
            'active',
            'company'
        )


class PhoneSerializer(serializers.ModelSerializer):
    """Для полной информации"""

    class Meta:
        model = models.Number
        exclude = (
            'id',
            'company'
        )


class CompanySerializer2(serializers.ModelSerializer):
    """Для краткой информацииж об компании"""
    class Meta:
        model = models.Company
        fields = ('name',
                  'image',
                  )


class ReviewSerializer(serializers.ModelSerializer):
    """Для краткой информацииж об компании"""
    class Meta:
        model = models.Review
        fields = '__all__'


class DiscountSerialzierDto(serializers.Serializer):
    """Для полной информации"""
    id = serializers.IntegerField()
    description = serializers.CharField()
    days = serializers.CharField()
    condition = serializers.CharField()
    work_hours = serializers.CharField()
    company = serializers.CharField()
    address = AddressSerializer()
    socials = SocialSerializer(many=True)
    phones = PhoneSerializer(many=True)
    views = serializers.IntegerField()
    instruction = serializers.CharField()
    percentage = serializers.IntegerField()
    image = serializers.URLField()
    # order_num = serializers.IntegerField()


class CouponSerializer(serializers.Serializer):

    titel = serializers.CharField(default='СКИДОЧНЫЙ КУПОН', required=False)
    company = serializers.CharField()
    percentage = serializers.IntegerField()
    description = serializers.CharField()
    time_limit = serializers.CharField()
    logo = serializers.SlugField()


class DiscountSerialzierDtoShort(serializers.Serializer):
    """Для краткой информации"""
    id = serializers.IntegerField()
    description = serializers.CharField()
    days = serializers.CharField()
    company = CompanySerializer2()
    views = serializers.IntegerField()
    percentage = serializers.IntegerField()
    # order_num = serializers.IntegerField()
    city = serializers.CharField()
    # city_order = serializers.IntegerField()


class PincodeValidationSerialzier(serializers.Serializer):
    pincode = serializers.CharField(min_length=4,
                                    max_length=4,
                                    validators=[validation_func.check_is_numeric,])


