from django.contrib import admin
from .models import ClickCounter, Order, Box, BoxTariff, Courier, Promo, Place
from django.conf import settings
from django.utils.html import format_html


@admin.register(ClickCounter)
class ClickCounterAdmin(admin.ModelAdmin):
    list_display = ('id', 'token', 'clicks', 'referral_link')
    readonly_fields = ('clicks', 'referral_link', 'token')
    search_fields = ('token',)


    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields
        return ['clicks']

    def referral_link(self, obj):
        url = f"{settings.SITE_URL}/?ref={obj.token}"
        return format_html(
            '<input type="text" value="{}" readonly style="width: 300px;" onclick="this.select()">'
            '<br><a href="{}" target="_blank">Перейти по ссылке</a>',
            url, url
        )

    referral_link.short_description = "Реферальная ссылка"

@admin.register(Place)
class OrderAdmin(admin.ModelAdmin):

    pass

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ['registered_at']
    fields = [
        'status',
        'start_storage',
        'end_storage',
        'cell',
        'cuser',
        'total_price',
        'node',
        'promo',
        'courier',
        'registered_at',
    ]

    pass

@admin.register(Courier)
class CourierAdmin(admin.ModelAdmin):
    pass

@admin.register(BoxTariff)
class BoxTariffAdmin(admin.ModelAdmin):
    pass

@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    pass

@admin.register(Promo)
class PromoAdmin(admin.ModelAdmin):
    list_display = ('name','discount','is_active')
    list_filter = ('is_active',)

@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    pass
