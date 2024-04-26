from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Products, Product, Shop

from .models import Medication

from .models import CartItem, OrderItem, Order

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['medication', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'created_at', 'status', 'total_cost', 'items']

class CartItemSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    class Meta:
        model = CartItem
        fields = ['id', 'medication', 'quantity', 'name', 'price']

    
    def get_name(self, obj):
        # Ensure that medication is related to obj and has a name attribute
        return obj.medication.name if obj.medication else "No Name"

    def get_price(self, obj):
        # Ensure that medication is related to obj and has a price attribute
        return obj.medication.price if obj.medication else 0.0

class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = '__all__' 

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class ProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ['id', 'itemName', 'description', 'price', 'quantity', 'image']

class ProductSerializer(serializers.ModelSerializer):
    shop_name = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'title', 'description','quantity', 'returned', 'location', 'category', 'shop_name')
    def get_shop_name(self, obj):
        if obj.shop:
            return obj.shop.shopname
        return None
    
    def create(self, validated_data):
        shop_id = self.context.get('shop_id')  # Get the shop_id from the context

        try:
            shop = Shop.objects.get(pk=shop_id)
        except Shop.DoesNotExist:
            raise serializers.ValidationError(f"Shop with ID {shop_id} does not exist.")

        validated_data['shop'] = shop  # Set the shop foreign key in the validated data
        return super(ProductSerializer, self).create(validated_data)

class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ('shop_owner', 'shopname', 'location', 'phone_no', 'email')
    def create(self, validated_data):
        shop = Shop.objects.create(
            shop_owner=validated_data['shop_owner'],
            shopname=validated_data['shopname'],
            location=validated_data['location'],
            phone_no=validated_data['phone_no'],
            email=validated_data['email']
        )
        return shop
