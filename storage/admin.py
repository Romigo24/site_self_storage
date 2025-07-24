from django.contrib import admin
from .models import ClickCounter
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