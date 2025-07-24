from django.db import models
from django.utils.crypto import get_random_string


class Place(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.name}, {self.address}'


class BoxTariff(models.Model):
    size = models.CharField(max_length=100)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.size}, цена: {self.price_per_day}'


class Box(models.Model):
    cell_size = models.ForeignKey(BoxTariff,
                                  on_delete=models.CASCADE)
    is_occupied = models.BooleanField(default=False)
    address = models.ForeignKey(Place, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.id}, {self.cell_size.size}'


class Client(models.Model):
    client_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=200)
    fio = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.client_name},'


class Order(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    contacts = models.CharField(max_length=100, blank=True)
    start_storage = models.DateField()
    end_storage = models.DateField()
    cell = models.ForeignKey(Box, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2,
                                      blank=True, null=True)

    def __str__(self):
        return f'{self.client.client_name}, {self.contacts}'

    def save(self, *args, **kwargs):
        price_per_day = self.cell.cell_size.price_per_day
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