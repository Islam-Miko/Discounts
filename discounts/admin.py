from django.contrib import admin

from . import models


class AddressTabularAdmin(admin.TabularInline):
    model = models.Address
    max_num = 1


class DiscountLimitAdmin(admin.TabularInline):
    model = models.DiscountLimit
    extra = 1
    max_num = 1


class SocialNetTabular(admin.TabularInline):
    model = models.SocialNet


class NumbersTabular(admin.TabularInline):
    model = models.Number


class CompanyAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    ordering = ('name',)
    list_filter = ('name',)
    inlines = [AddressTabularAdmin,SocialNetTabular, NumbersTabular]


class DiscountAdmin(admin.ModelAdmin):
    model = models.Discount
    inlines = [DiscountLimitAdmin]


admin.site.register(models.Client)
admin.site.register(models.City)
admin.site.register(models.Category)
admin.site.register(models.ClientDiscount)
admin.site.register(models.Company, CompanyAdmin)
admin.site.register(models.Discount, DiscountAdmin)
admin.site.register(models.Description)
admin.site.register(models.WatchedAmount)
# admin.site.register(models.SocialNet)
# admin.site.register(models.Number)
# admin.site.register(models.Address)
admin.site.register(models.Review)
admin.site.register(models.Instruction)

