from django.contrib import admin
from .models import Product, Shop, Medication, Cart, CartItem, Order, Profile

admin.site.register(Product)
admin.site.register(Shop)
admin.site.register(Medication)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(Profile)
# Register your models here.
