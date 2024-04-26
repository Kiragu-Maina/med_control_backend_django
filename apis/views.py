from django.http import JsonResponse
from django.db.models import Avg
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from rates.utils import utility
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .serializers import UserSerializer, ProductsSerializer, ProductSerializer, ShopSerializer, MedicationSerializer
from .models import Products, Product, Shop, Medication, Cart, CartItem
from .models import Cart, Order, OrderItem
from .serializers import OrderSerializer, CartItemSerializer
from django.shortcuts import get_object_or_404
from .serializers import CartItemSerializer 
from django_eventstream import send_event
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .models import Profile

class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user
        try:
            profile = user.profile  # Access the related Profile
            user_data = {
                'name': user.username,  # or user.get_full_name() if you use the full name
                'email': user.email,
                'about': profile.about,  # Correctly access 'about' from the user's profile
            }
            return Response(user_data)
        except Profile.DoesNotExist:
            # Handle case where user profile does not exist
            raise Http404("User profile not found")

class CartItemsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            cart = Cart.objects.get(user=user)
            cart_items = CartItem.objects.filter(cart=cart)
            
            serializer = CartItemSerializer(cart_items, many=True)
            # from serializer.data get medication.itemName then append as name to response
            return Response(serializer.data)
        except Cart.DoesNotExist:
            return Response({"message": "No cart found for this user"}, status=404)
        
class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        cart = Cart.objects.get(user=user)
        cart_items = cart.items.all()

        if not cart_items:
            return Response({'error': 'Your cart is empty'}, status=400)

        # Create an order
        order = Order.objects.create(user=user)
        total_cost = 0

        # Move items from cart to order
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                medication=item.medication,
                quantity=item.quantity,
                price=item.medication.price
            )
            total_cost += item.medication.price * item.quantity

        order.total_cost = total_cost
        order.save()

        # Clear the cart
        cart.items.all().delete()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=201)


class OrderStatementView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    
class AddToCartView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user

        medication_id = request.data.get('medication_id')
        requested_quantity = int(request.data.get('quantity', 1))

        medication = get_object_or_404(Medication, pk=medication_id)

        # Check if requested quantity exceeds available stock
        if requested_quantity > medication.stock_quantity:
            return Response({"error": "Not enough stock available"}, status=status.HTTP_400_BAD_REQUEST)

        cart, created = Cart.objects.get_or_create(user=user)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            medication=medication,
            defaults={'quantity': requested_quantity},
        )
        if not created:
            # Update the quantity if adding more of an existing item
            new_quantity = cart_item.quantity + requested_quantity
            # Check again for the total quantity against stock
            if new_quantity > medication.stock_quantity:
                return Response({"error": "Not enough stock available for the total requested quantity"}, status=status.HTTP_400_BAD_REQUEST)
            cart_item.quantity = new_quantity
            cart_item.save()

        
        medication.stock_quantity -= requested_quantity
        medication.save()

        return Response({"message": "Medication added to cart successfully"})

class MedicationViewSet(viewsets.ModelViewSet):
    queryset = Medication.objects.all()
    serializer_class = MedicationSerializer
    
class ProductListView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            email = serializer.validated_data['email']
            User.objects.create_user(username=username, email=email, password=password)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            request.session['logged_in_user'] = username
            token, _ = Token.objects.get_or_create(user=user)

            # Include the token in the response data
            return Response({'token': token.key, 'message': 'Logged in successfully.'})
        
            
        return Response({'message': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)


class ShopInventoryView(APIView):
    authentication_classes = []
    permission_classes = []
    
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        inventory_data = {
            'cement_price__avg': Product.objects.filter(title='cement').aggregate(Avg('price'))['price__avg'] or 0,
            'sand_price__avg': Product.objects.filter(title='sand').aggregate(Avg('price'))['price__avg'] or 0,
            'aggregate_price__avg': Product.objects.filter(title='aggregate').aggregate(Avg('price'))['price__avg'] or 0,
        }

        response_data = {
            'cement_price_avg': inventory_data['cement_price__avg'],
            'sand_price_avg': inventory_data['sand_price__avg'],
            'aggregate_price_avg': inventory_data['aggregate_price__avg'],
        }

        return Response(response_data, status=status.HTTP_200_OK)

class ComponentsView(APIView):
    authentication_classes = []
    permission_classes = []
    
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        components = ['Concrete', 'Bricks', 'Steel']
        return Response(components)
class CategoriesView(APIView):
    authentication_classes = []
    permission_classes = []
    
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        categories = [
                'AK47',
                'M3',
                'G3',
                '9mm',
                '16mm'
                
             
            ]

        
        return Response(categories)



class RatesView(APIView):
    authentication_classes = []
    permission_classes = []

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        component = data['component']
        selected_class = data['class']
        labour_costs = data['labourCosts']
        profit_overheads = data['profitOverheads']
        print('component:', component, 'selected_class:', selected_class, 'labour_costs:', labour_costs, 'profit_overheads: ',profit_overheads)
        
        # Process the data and calculate the rate
        rate = utility(component=component, selected_class=selected_class, labour_costs=labour_costs, profit_overheads=profit_overheads)
        print(rate)
        return JsonResponse(rate)

class ProductsUpload(APIView):
    authentication_classes = []
    permission_classes = []

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        data_list = request.data
        print(data_list)  # Assuming request.data is a list of dictionaries
        username = self.kwargs.get('username', None)

        # shop_name = request.session.get('shop_name')
        shop = Shop.objects.filter(shop_owner=username).first()

  # Assign the Shop object's ID to the 'shop' field
        context = {'shop_id': shop.id}  # Provide the shop_id in the context
        for data in data_list:
            serializer = ProductSerializer(data=data, context=context)

            
            print(serializer)
            if serializer.is_valid():
                serializer.save()
                send_event('test', 'message', {'text': 'hello world'})  # Create and save the product objects
                
            else:
                print(serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Items created successfully.'}, status=status.HTTP_201_CREATED)
    
    def put(self, request, *args, **kwargs):
        print('put called')
        product_id = self.kwargs.get('product_id', None)  # Assuming you have a URL parameter for product_id
        print(product_id)
        username = self.kwargs.get('username', None)
        print(username)
        shop = Shop.objects.filter(shop_owner=username).first()

        context = {'shop_id': shop.id}
        try:
            product = Product.objects.get(id=product_id, shop=shop)
        except Product.DoesNotExist:
            return Response({'message': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product, data=request.data, context=context, partial=True)
        if serializer.is_valid():
            serializer.save()
            send_event('test', 'message', {'text': 'hello world'})
            return Response({'message': 'Product updated successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        product_id = self.kwargs.get('product_id', None)  # Assuming you have a URL parameter for product_id
        username = self.kwargs.get('username', None)
        shop = Shop.objects.filter(shop_owner=username).first()

        try:
            product = Product.objects.get(id=product_id, shop=shop)
        except Product.DoesNotExist:
            return Response({'message': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

        product.delete()
        send_event('test', 'message', {'text': 'hello world'})
        return Response({'message': 'Product deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)


class ProductsView(APIView):
    authentication_classes = []
    permission_classes = []
    
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self, request):
        print(request)
        username = self.kwargs.get('username', None)
        if username != 'none':

       
            shop_name = Shop.objects.filter(shop_owner=username).values_list('shopname', flat=True).first()
            request.session['shop_name'] = shop_name
            print('shopname in productsview is: ', shop_name)

            if shop_name is not None:
                # Do something with the shop_name
                print(f"The shop name in session is: {shop_name}")
                queryset = Product.objects.filter(shop__shopname=shop_name)
                print(queryset)
            else:
                # Handle the case when the shop_name is not found in the session
                queryset = Product.objects.all()
        else:
            queryset = Product.objects.all()
            print(queryset)

     
        return queryset

    def get(self, request, *args, **kwargs):
        username = self.kwargs.get('username', None)
        if username != 'none':

       
            shop_name = Shop.objects.filter(shop_owner=username).values_list('shopname', flat=True).first()
            request.session['shop_name'] = shop_name
            print('shopname in productsview is: ', shop_name)

            if shop_name is not None:
                # Do something with the shop_name
                print(f"The shop name in session is: {shop_name}")
                queryset = Product.objects.filter(shop__shopname=shop_name)
                print(queryset)
                serializer = ProductSerializer(queryset, many=True)
        
                return Response(serializer.data)
            else:
                # Handle the case when the shop_name is not found in the session
                queryset = Product.objects.all()
        else:
            queryset = Product.objects.all()
            serializer = ProductSerializer(queryset, many=True)
   
        dict_data = []
        for item in serializer.data:
            data_item = {
                'user': item['shop_name'],
                'type': item['category'],
                'taken': item['quantity'],
                'returned': item['returned']
            }
            if item['title'] == 'firearm':
                data_item['item_type'] = 'firearm'
            else:
                data_item['item_type'] = 'ammunition'
            dict_data.append(data_item)

        print(dict_data)
        return Response(dict_data)

        
        

class CreateShop(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = ShopSerializer(data=request.data)
        print(serializer)
        if serializer.is_valid():
            shop = serializer.save()  # Create and save the shop object
            # Additional logic or response handling
            return JsonResponse(serializer.data, status=200)
        else:
            errors = serializer.errors
            return JsonResponse(errors, status=400)
        

class CheckShop(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self, request, *args, **kwargs):
        username = kwargs['username']  # Assuming 'username' is part of the URL path parameter
        # Handle the 'GET' request logic here
        # Example: Retrieve data or perform any necessary operations
        # You can use the 'username' to fetch the corresponding data from the database
        # Replace 'Shop.objects.get()' with the appropriate query to retrieve the shop_owner based on 'username'
        try:
            exists = Shop.objects.filter(shop_owner=username).exists()

            if exists:
                print('exists')
                try:
                    shop_name = Shop.objects.filter(shop_owner=username).values_list('shopname', flat=True).first()

                    if shop_name is not None:
                        # Do something with the shop_name
                        print(f"The shop name in session is: {shop_name}")
                        request.session['shop_name'] = shop_name
                        request.session.save()
                    else:
                        
                        # Handle the case when the shop_name is not found in the session
                        print("Shop name not found for the given username.")
                except Exception as e:
                    print(f"Error occurred during database query: {e}")
                
            return JsonResponse({'exists': exists, 'shopname':shop_name}, status=200)   
        except:
            return JsonResponse({'exists': False}, status=400)  

      


    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
       
        return super().dispatch(request, *args, **kwargs)
    

class HandleReturnView(APIView):
    authentication_classes = []
    permission_classes = []
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    
    def post(self, request, *args, **kwargs):
            data = request.data
            print(data)
            shopname=data.get('shopname')
            shop = Shop.objects.get(shopname=shopname)
            print(shop)
            
            product_id = data.get('productId')
            print(product_id)
            quantity_to_return = data.get('QuantityToReturn')

            try:
                product = Product.objects.get(shop=shop)
               
                product.returned = quantity_to_return
                product.save()
            except Product.DoesNotExist:
                return Response({'error': f'Product with ID {product_id} not found'}, status=status.HTTP_404_NOT_FOUND)
        
            return Response({'message': 'Items returned successfully.'}, status=status.HTTP_201_CREATED)
