from django.db import models


class Shop(models.Model):
    shopname = models.CharField(max_length=255)
    location = models.CharField(max_length=255)

    def __str__(self):
        return f'Shop {self.id}: {self.shopname}: {self.location}'


class Inventory(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    cement_price = models.DecimalField(max_digits=10, decimal_places=2)
    sand_price = models.DecimalField(max_digits=10, decimal_places=2)
    aggregate_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Inventory of {self.shop.shopname} ({self.shop.location})"
