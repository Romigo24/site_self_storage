from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    password = None

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            'first_name',
            'last_name',
            'username',
            'phone',
            'address',
            'password1',
            'password2'
        )
