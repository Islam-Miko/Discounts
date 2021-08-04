from rest_framework import serializers
from . import models


class DescriptionSerializer(serializers.ModelSerializer):
    """Для  краткой информации"""

    class Meta:
        model = models.Description
        fields = ('description',
                  'days')


class DescriptionSerializer2(serializers.ModelSerializer):
    """Для полной информации"""

    class Meta:
        model = models.Description
        fields = ('description',
                  'days',
                  'condition',
                  'work_hours')


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


class CompanySerializer(serializers.ModelSerializer):
    """Для полной информацииж об компании"""
    addresses = AddressSerializer(many=True)
    socials = SocialSerializer(many=True)
    phones = PhoneSerializer(many=True)

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
    description = DescriptionSerializer2()
    company = CompanySerializer()
    views = serializers.IntegerField()
    instruction = serializers.SlugRelatedField(slug_field='text', queryset=models.Instruction.objects.all())

    class Meta:
        model = models.Discount
        exclude = (
            'start_date',
            'end_date',
            'pincode',
            'active',
            'category'
        )


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
                  'city',
                  'order_num',
                  'city_order'
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


class ClientDiscountSerializer(serializers.Serializer):

    discount = serializers.SlugRelatedField(slug_field='id',
                                            queryset=models.Discount.objects.all(),
                                            required=False)
    client = serializers.SlugRelatedField(slug_field='id',
                                            queryset=models.Client.objects.all(),
                                            required=False)

    pincode = serializers.CharField(required=True, max_length=4,
                                    min_length=4)

    def update(self, instance, validated_data):
        pincode = validated_data.get('pincode')
        instance.discount = validated_data.get('discount', instance.discount)
        instance.client = validated_data.get('client', instance.client)
        discount_ = models.Discount.objects.filter(id=instance.discount.id).get()
        if discount_.pincode == pincode:
            instance.status = models.ClientDiscount.STATUS[2][0]
        else:
            return instance
        instance.save()
        return instance


class PincodeValidationSerialzier(serializers.Serializer):
    pincode = serializers.CharField(min_length=4,
                                    max_length=4)


