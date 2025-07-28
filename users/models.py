from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class CustomUser(AbstractUser):
    phone = PhoneNumberField(
        verbose_name='Мобильный номер',
        region='RU',
        unique=True
    )
    address = models.CharField(
        'Адрес',
        max_length=250
    )
    photo = models.ImageField(
        'Фото',
        upload_to='photos/',
        default = 'photos/unnamed.jpg',
        blank=True,
        null=True
    )
    email = models.EmailField(
        'Почта',
        unique=True
    )

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    def save(self, *args, **kwargs):
        if not self.email and self.username:
            self.email = self.username
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.first_name} {self.last_name} {self.phone}'