from django.db import models
from django.utils.crypto import get_random_string
from users.models import CustomUser

class Courier(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=17)
    vehicle_type = models.CharField(max_length=50, choices=[
        ('car', 'Автомобиль'),
        ('bicycle', 'Велосипед'),
        ('foot', 'Пеший'),
    ], default='car')
    is_active = models.BooleanField(default=True)
    class Meta:
        verbose_name='Курьер'
        verbose_name_plural='Курьеры'

    def __str__(self):
        return f"{self.name} ({self.get_vehicle_type_display()})"




class Promo(models.Model):
    name = models.CharField(max_length=100)
    discount = models.DecimalField(decimal_places=2, max_digits=5)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name='Акция'
        verbose_name_plural='Акции'

    def __str__(self):
        return f"{self.name} {self.discount}%"


class Place(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    is_show = models.BooleanField(default=False, blank=True, null=True)

    class Meta:
        verbose_name='Склад'
        verbose_name_plural='Склады'

    def __str__(self):
        return f'{self.name}, {self.address}'


class BoxTariff(models.Model):
    size = models.CharField(max_length=100)
    price_per_month = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name='Тариф'
        verbose_name_plural='Тариф'

    def __str__(self):
        return f'{self.size}, цена: {self.price_per_month}'


class Box(models.Model):
    cell_size = models.ForeignKey(BoxTariff,
                                  on_delete=models.CASCADE)
    is_occupied = models.BooleanField(default=False)
    address = models.ForeignKey(Place, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name='Бокс'
        verbose_name_plural='Бокс'

    def __str__(self):
        return f'{self.id}, {self.cell_size.size}'



class Order(models.Model):
    contacts = models.CharField(max_length=100, blank=True)
    start_storage = models.DateField()
    end_storage = models.DateField()
    cell = models.ForeignKey(Box, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2,
                                      blank=True, null=True)
    node = models.TextField(null=True, blank=True)
    promo = models.ForeignKey(Promo, on_delete=models.CASCADE, null=True, blank=True)
    cuser = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name='Заказ'
        verbose_name_plural='Заказы'

    courier = models.ForeignKey(
        Courier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )

    def __str__(self):
        return f'{self.cuser.username}, {self.contacts}'

    #Добавить подсчет промокода
    def save(self, *args, **kwargs):
        price_per_day = self.cell.cell_size.price_per_month
        days = (self.end_storage - self.start_storage).days
        self.total_price = days * price_per_day
        super().save(*args, **kwargs)


class ClickCounter(models.Model):
    token = models.CharField(max_length=20, unique=True, default=get_random_string(length=20))
    clicks = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.id}: {self.clicks} clicks"

    def get_absolute_url(self, request):
        return f"{request.scheme}://{request.get_host()}/?ref={self.token}"


