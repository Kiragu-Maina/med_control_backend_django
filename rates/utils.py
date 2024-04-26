from django.db.models import Avg
from .models import Shop, Inventory
from apis.models import Product

def utilities(request):
    return concrete(request)


def concrete(request):

    CementPrice = float(Inventory.objects.aggregate(Avg('cement_price'))[
        'cement_price__avg'])
    SandPrice = float(Inventory.objects.aggregate(
        Avg('sand_price'))['sand_price__avg'])
    AggregatePrice = float(Inventory.objects.aggregate(Avg('aggregate_price'))[
        'aggregate_price__avg'])
    print('cementprice:', CementPrice, ' sandprice:',
          SandPrice, ' aggregateprice:', AggregatePrice)

    CementUnitsperTon = request.POST.get('CementUnitsperTon')
    if CementUnitsperTon is not None and CementUnitsperTon != '':
        CementUnitsperTon = float(CementUnitsperTon)
    else:
        # handle the case where the CementUnitsperTon value is missing or empty
        CementUnitsperTon = 0.0  # set a default value or raise an error

    SandUnitsperTon = request.POST.get('SandUnitsperTon')
    if SandUnitsperTon is not None and SandUnitsperTon != '':
        SandUnitsperTon = float(SandUnitsperTon)
    else:
        # handle the case where the SandUnitsperTon value is missing or empty
        SandUnitsperTon = 0.0  # set a default value or raise an error

    AggregateUnitsperTon = request.POST.get('AggregateUnitsperTon')
    if AggregateUnitsperTon is not None and AggregateUnitsperTon != '':
        AggregateUnitsperTon = float(AggregateUnitsperTon)
    else:
        # handle the case where the AggregateUnitsperTon value is missing or empty
        AggregateUnitsperTon = 0.0  # set a default value or raise an error

    num = request.POST.get('num')
    if num is not None and num != '':
        num = float(num)
        num = 0.01*num
    else:
        # handle the case where the num value is missing or empty
        num = 0.0  # set a default value or raise an error

    # CementPrice = float(request.POST.get('CementPrice'))
    # SandPrice = float(request.POST.get('SandPrice'))
    # AggregatePrice = float(request.POST.get('AggregatePrice'))
    # CementUnitsperTon = float(request.POST.get('CementUnitsperTon'))
    # SandUnitsperTon = float(request.POST.get('SandUnitsperTon'))
    # AggregateUnitsperTon = float(request.POST.get('AggregateUnitsperTon'))
    # num = float(request.POST.get('num'))
    ratios = {
        '15': [1, 3, 6],
        '20': [1, 2, 4],
        '25': [1, 1.5, 3],
        '30': [1, 1, 2]
    }

    concreteclass = request.POST.get('class')
    print(concreteclass)
    ratio = ratios.get(concreteclass)
    print(ratio)

    if ratio is None:
        ratio = [1, 1, 1]
        # raise ValueError('Invalid concrete class')
    TotalRatio = sum(ratio)
    print('sumratio:', TotalRatio)
    ComponentCement = 1.485 * CementUnitsperTon * CementPrice * ratio[0]
    ComponentSand = 1.605 * SandUnitsperTon * SandPrice * ratio[1]
    ComponentAggregate = 1.415 * \
        AggregateUnitsperTon * AggregatePrice * ratio[2]

    TotalCostof7cmofconcrete = ComponentCement + ComponentAggregate + ComponentSand
    print(TotalCostof7cmofconcrete)
    CostperCm = TotalCostof7cmofconcrete/TotalRatio
    print(CostperCm)
    addshrinkage = CostperCm + (0.45*CostperCm)
    print(addshrinkage)
    addlabour = addshrinkage + (0.3*addshrinkage)
    print(addlabour)
    addoverhead = addlabour + (num*addlabour)
    print(addoverhead)
    addVAT = addoverhead + (0.16*addoverhead)
    print(addVAT)
    ratepersm = addVAT

    context = {'ratepersm': ratepersm}
    return context


def utility(component, selected_class, labour_costs, profit_overheads):
    print('utility called')
    if component == 'Concrete':
        print('component is concrete')
        return concret(selected_class, labour_costs, profit_overheads)
    elif component == 'Steel':
        return steel(labour_costs, profit_overheads)


def steel(labour_costs, profit_overheads):
    priceofreinforcement = 103
    priceoftiewireper25kg = 4500

    mmdiameterbars = 1000 * priceofreinforcement
    Wasteandlaps = 0.05 * mmdiameterbars
    Unloadandstack = 75 + mmdiameterbars + Wasteandlaps
    Tiewire = Unloadandstack + (priceoftiewireper25kg/25 * 7)
    Spacers = Tiewire + 2000
    labour = Spacers + ((labour_costs/8 * 28) + (labour_costs/8 * 30))
    profits = labour + (profit_overheads/100 * labour)
    vat = profits + (0.16*profits)
    ratepersm = (vat/1000)
    context = {'ratepersm': ratepersm}
    return context


def concret(selected_class, labour_costs, profit_overheads):
    
    CementPrice = float(Product.objects.filter(title__iexact='cement').aggregate(Avg('price'))['price__avg'] or 0)
    SandPrice = float(Product.objects.filter(title__iexact='sand').aggregate(Avg('price'))['price__avg'] or 0)
    AggregatePrice = float(Product.objects.filter(title__iexact='aggregate').aggregate(Avg('price'))['price__avg'] or 0)
    print('cementprice:', CementPrice, ' sandprice:',
          SandPrice, ' aggregateprice:', AggregatePrice)

    CementUnitsperTon = 20
    if CementUnitsperTon is not None and CementUnitsperTon != '':
        CementUnitsperTon = float(CementUnitsperTon)
    else:
        # handle the case where the CementUnitsperTon value is missing or empty
        CementUnitsperTon = 0.0  # set a default value or raise an error

    SandUnitsperTon = 1
    if SandUnitsperTon is not None and SandUnitsperTon != '':
        SandUnitsperTon = float(SandUnitsperTon)
    else:
        # handle the case where the SandUnitsperTon value is missing or empty
        SandUnitsperTon = 0.0  # set a default value or raise an error

    AggregateUnitsperTon = 1
    if AggregateUnitsperTon is not None and AggregateUnitsperTon != '':
        AggregateUnitsperTon = float(AggregateUnitsperTon)
    else:
        # handle the case where the AggregateUnitsperTon value is missing or empty
        AggregateUnitsperTon = 0.0  # set a default value or raise an error

    # CementPrice = float(request.POST.get('CementPrice'))
    # SandPrice = float(request.POST.get('SandPrice'))
    # AggregatePrice = float(request.POST.get('AggregatePrice'))
    # CementUnitsperTon = float(request.POST.get('CementUnitsperTon'))
    # SandUnitsperTon = float(request.POST.get('SandUnitsperTon'))
    # AggregateUnitsperTon = float(request.POST.get('AggregateUnitsperTon'))
    # num = float(request.POST.get('num'))
    ratios = {
        '15': [1, 3, 6],
        '20': [1, 2, 4],
        '25': [1, 1.5, 3],
        '30': [1, 1, 2]
    }

    concreteclass = selected_class
    print(concreteclass)
    ratio = ratios.get(concreteclass)
    print(ratio)

    if ratio is None:
        ratio = [1, 1, 1]
        # raise ValueError('Invalid concrete class')
    TotalRatio = sum(ratio)
    print('sumratio:', TotalRatio)
    ComponentCement = 1.485 * CementUnitsperTon * CementPrice * ratio[0]
    ComponentSand = 1.605 * SandUnitsperTon * SandPrice * ratio[1]
    ComponentAggregate = 1.415 * \
        AggregateUnitsperTon * AggregatePrice * ratio[2]

    TotalCostof7cmofconcrete = ComponentCement + ComponentAggregate + ComponentSand
    print(TotalCostof7cmofconcrete)
    CostperCm = TotalCostof7cmofconcrete/TotalRatio
    print(CostperCm)
    addshrinkage = CostperCm + (0.45*CostperCm)
    print(addshrinkage)

    addlabour = addshrinkage + (0.01*labour_costs*addshrinkage)
    print(addlabour)

    addoverhead = addlabour + (0.01*profit_overheads*addlabour)
    print(addoverhead)
    addVAT = addoverhead + (0.16*addoverhead)
    print(addVAT)
    ratepersm = addVAT

    context = {'ratepersm': ratepersm}
    return context
