from rest_framework import serializers
from . import models


class DescriptionSerializer(serializers.ModelSerializer):
    """Для полной информации"""

    class Meta:
        model = models.Description
        fields = ('description',
                  'days')


class AddressSerializer(serializers.ModelSerializer):
    """Для полной информации"""
    city = serializers.SlugRelatedField(slug_field='city', queryset=models.City.objects.all())

    class Meta:
        model = models.Address
        fields = '__all__'


class SocialSerializer(serializers.ModelSerializer):
    """Для полной информации"""
    class Meta:
        model = models.SocialNet
        exclude = (
            'id',
            'active'
        )


class PhoneSerializer(serializers.ModelSerializer):
    """Для полной информации"""

    class Meta:
        model = models.Number
        exclude = (
            'id',
        )


class CompanySerializer(serializers.ModelSerializer):
    """Для полной информацииж об компании"""
    address = AddressSerializer()
    social_net = SocialSerializer()
    phone_number = PhoneSerializer()

    class Meta:
        model = models.Company
        # fields = ('name',
        #           'phone_number',
        #           'social_net'
        #           'days')
        exclude = (
            'image',
        )


class CompanySerializer2(serializers.ModelSerializer):
    """Для краткой информацииж об компании"""
    class Meta:
        model = models.Company
        fields = ('name',
                  'image',
                  )


class DiscountSerialzier(serializers.ModelSerializer):
    """Для полной информации"""
    description = DescriptionSerializer()
    company = CompanySerializer()
    class Meta:
        model = models.Discount
        fields = ('percentage',
                  'id',
                  'description',
                  'company')


class DiscountShortSerialzier(serializers.ModelSerializer):
    """Для краткой информации"""
    description = DescriptionSerializer()
    company = CompanySerializer2()
    views = serializers.IntegerField()
    city = serializers.SlugField()

    class Meta:
        model = models.Discount
        fields = ('percentage',
                  'id',
                  'description',
                  'company',
                  'views',
                  'city'
                  )