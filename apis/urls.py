"""conrates URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, include
from .views import ShopInventoryView, ComponentsView, RatesView, RegisterView, LoginView, ProductsView, ProductsUpload, ProductListView, CheckShop, CreateShop, CategoriesView, HandleReturnView, AddToCartView, CreateOrderView
from .views import MedicationViewSet, CartItemsView, OrderStatementView, UserInfoView
# from django.urls import path, include
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'medications', MedicationViewSet)
# router.register(r'addtocart', AddToCartView)



urlpatterns = [
    
    path('shop-inventory/', ShopInventoryView.as_view(), name='shop-inventory'),
    path('components/', ComponentsView.as_view(), name='components'),
    path('rates/', RatesView.as_view(), name='rates'),
    path('register/', RegisterView.as_view(), name='api-register'),
    path('login/', LoginView.as_view(), name='api-login'),
    path('products/<str:username>/<int:product_id>/', ProductsUpload.as_view(), name='uploadproducts'),
    path('ecommerce/<str:username>/', ProductsView.as_view(), name='ecommerce'),
    path('checkshop/<str:username>/', CheckShop.as_view(), name='checkshop'),
    path('createshop/', CreateShop.as_view(), name='createshop'),   
    path('categories/', CategoriesView.as_view(), name='categories'),
    path('return/', HandleReturnView.as_view(), name='return'),
    path('addtocart/', AddToCartView.as_view(), name='add-to-cart'),
    path('create-order/', CreateOrderView.as_view(), name='create-order'),
    path('cart/items/', CartItemsView.as_view(), name='cart-items'),
    path('orders/', OrderStatementView.as_view(), name='order-statement'),
    path('user/info/', UserInfoView.as_view(), name='user-info'),
    path('', include(router.urls)),
]   
