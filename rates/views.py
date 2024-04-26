
from .utils import utilities

from .models import Shop, Inventory
from django.shortcuts import render, redirect
from .models import Shop, Inventory


def shop_inventory(request, shop_id=None):
    if shop_id is None:
        shops = Shop.objects.all()
        inventory_data = []
        for shop in shops:
            print(shop)

            inventory = Inventory.objects.get(shop=shop)
            inventory_list = {
                'shop': inventory.shop,
                'cement_price': inventory.cement_price,
                'sand_price': inventory.sand_price,
                'aggregate_price': inventory.aggregate_price,
            }
            inlist = (shop, inventory_list)
            inventory_data.append(inlist)
        return render(request, 'shops.html', {
            'shops': shops,
            'inventory_data': inventory_data,
        })
    else:
        shop = Shop.objects.get(id=shop_id)
        inventory = Inventory.objects.get(shop=shop)
        return render(request, 'shops.html', {
            'shop': shop,
            'cement_price': inventory.cement_price,
            'sand_price': inventory.sand_price,
            'aggregate_price': inventory.aggregate_price,
        })


def update_inventory(request):
    if request.method == 'POST':
        shop_id = request.POST.get('shop_id')
        inventory = Inventory.objects.get(shop_id=shop_id)

        # update the inventory data based on the form input
        inventory.cement_price = request.POST.get('cement_price')
        inventory.sand_price = request.POST.get('sand_price')
        inventory.aggregate_price = request.POST.get('aggregate_price')
        inventory.save()

        return redirect('shop_inventory')

    else:
        # if the request method is GET, render the update form
        shop_id = request.GET.get('shop_id')
        shop = Shop.objects.get(id=shop_id)
        inventory = Inventory.objects.get(shop=shop)

        return render(request, 'update_inventory.html', {
            'shop': shop,
            'inventory': inventory,
        })

        # Create your views here.


def rates(request):
    context = utilities(request)
    return render(request, 'index.html', context)
