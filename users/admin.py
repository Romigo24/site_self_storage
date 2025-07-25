from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {
            'fields': (
                'first_name',
                'last_name',
                'phone',
                'address',
                'photo',
            )
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'first_name',
                'last_name',
                'phone',
                'address',
                'photo',
                'password1',
                'password2',
            ),
        }),
    )

    list_display = (
        'username', 'first_name', 'last_name',
        'phone'
    )
    search_fields = ('username', 'first_name', 'last_name', 'phone')
    ordering = ('username',)