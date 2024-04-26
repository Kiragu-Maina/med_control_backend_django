from django.db import models
import random
import re
from PIL import Image
from io import BytesIO
from django.core.files import File
from django.contrib.auth.models import User  # Import the User model


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    about = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return self.user.username
    
class Medication(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    dosage = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField()

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at the time of order

    def __str__(self):
        return f"{self.quantity} of {self.medication.name}"

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

class Products(models.Model):
    itemName = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.CharField(max_length=255)  # Specify the max_length for the quantity field
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return self.itemName

def upload_location(instance, filename):
    ext = filename.split(".")[-1]
    shop = re.sub(r'\W+', '', instance.shop.shopname)
    item_name = re.sub(r'\W+', '', instance.title)
    category = re.sub(r'\W+', '', instance.category)
    num = random.randint(1000, 9999)

    filename = "{}.{}.{}".format(item_name, category, num)

    return "{}/{}.{}".format(shop, filename, ext)


class Shop(models.Model):
    shop_owner = models.CharField(max_length=255, default='null')
    shopname = models.CharField(max_length=255, default='null')
    location = models.CharField(max_length=255, default='null')
    phone_no = models.CharField(max_length=255, default='null')
    email = models.CharField(max_length=255, default='null')

    def __str__(self):
        return f'Shop {self.id}: {self.shopname}: {self.location} : {self.shop_owner} : {self.email}'


class Product(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, null=True)
    
    title = models.CharField(max_length=100)
    
    description = models.TextField()
    location = models.CharField(max_length=100, default='null')
    quantity = models.IntegerField(default=0)
    returned = models.IntegerField(default=0)
    

    
    category = models.CharField(max_length=100)
    def save(self, *args, **kwargs):
        if self.shop:
            self.location = self.shop.location  # Assign the location from the associated shop
       
            

            
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @classmethod
    def create_product_with_shop(cls, shop_id, **kwargs):
        try:
            shop = Shop.objects.get(pk=shop_id)
        except Shop.DoesNotExist:
            raise ValueError(f"Shop with ID {shop_id} does not exist.")

        product = cls(shop=shop, **kwargs)
        product.save()
        return product

    
