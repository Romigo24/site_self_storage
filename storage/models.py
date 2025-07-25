from django.db import models
from django.utils.crypto import get_random_string
from users.models import CustomUser
from datetime import date
from phonenumber_field.modelfields import PhoneNumberField

class Courier(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Имя'
    )
    PhoneNumberField(
        region='RU',
        unique=True,
        verbose_name='Мобильный номер',
    )
    vehicle_type = models.CharField(
        max_length=50,
        choices=[
            ('car', 'Автомобиль'),
            ('bicycle', 'Велосипед'),
            ('foot', 'Пеший'),
        ],
        default='car',
        verbose_name='Тип доставки',
    )
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.name} ({self.get_vehicle_type_display()})"


class Promo(models.Model):
    name = models.CharField(max_length=100)
    discount = models.DecimalField(decimal_places=2, max_digits=5)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} {self.discount}%"


class Place(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(
        max_length=100,
        verbose_name='Название склада'
    )
    address = models.CharField(
        max_length=200,
        verbose_name='Адрес'
    )
    is_show = models.BooleanField(default=False, blank=True, null=True)

    def __str__(self):
        return f'{self.name}, {self.address}'


class BoxTariff(models.Model):
    size = models.CharField(
        max_length=100,
        verbose_name='Размер бокса, м2'
    )
    price_per_month = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена аренды, руб.'
    )

    def __str__(self):
        return f'Размер, м2: {self.size}; цена, руб.: {self.price_per_month}'


class Box(models.Model):
    cell_size = models.ForeignKey(
        BoxTariff,
        on_delete=models.CASCADE,
        verbose_name='Размер бокса, м2'
    )
    address = models.ForeignKey(
        Place,
        on_delete=models.CASCADE,
        null=True,
        verbose_name='Адрес Склада'
    )
    is_occupied = models.BooleanField(
        default=False,
        verbose_name='Бокс занят'
    )

    def __str__(self):
        status = "занят" if self.is_occupied else "свободен"
        return f'№ {self.id}, размер: {self.cell_size.size} м2 - ({status})'


class Order(models.Model):
    STATUS_CHOICES = [
        ('unprocessed', 'Необработанный'),
        ('underway', 'В работе'),
        ('delivery', 'Доставка'),
        ('completed', 'Завершен'),
    ]
    start_storage = models.DateField(verbose_name='Начало аренды')
    end_storage = models.DateField(verbose_name='Конец аренды')
    cell = models.ForeignKey(
        Box,
        on_delete=models.CASCADE,
        verbose_name='Бокс'
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Цена, руб.'
    )
    node = models.TextField(
        null=True,
        blank=True,
        verbose_name='Перечень вещей на хранение'
    )
    promo = models.ForeignKey(
        Promo,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Промокод'
    )
    cuser = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Клиент'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='unprocessed',
        db_index=True,
        verbose_name='Статус'
    )
    courier = models.ForeignKey(
        Courier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name='Курьер'
    )
    registered_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Зарегистрирован',
        db_index=True
    )

    def __str__(self):
        return f'{self.cuser.first_name}, {self.cuser.phone}'

    #Добавить подсчет промокода
    def save(self, *args, **kwargs):
        price_per_day = self.cell.cell_size.price_per_month
        days = (self.end_storage - self.start_storage).days
        self.total_price = days * price_per_day
        super().save(*args, **kwargs)

    @property
    def days_left(self):
        if self.end_storage:
            return (self.end_storage - date.today()).days
        return None



class ClickCounter(models.Model):
    token = models.CharField(
        max_length=20,
        unique=True,
        default=get_random_string(length=20)
    )
    clicks = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.id}: {self.clicks} clicks"

    def get_absolute_url(self, request):
        return f"{request.scheme}://{request.get_host()}/?ref={self.token}"


