from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from .forms import CreateOrderForm
from django.views.decorators.http import  require_GET, require_POST
from urllib.parse import unquote
from django.contrib.auth.decorators import login_required
from .models import Box, Place, Promo, Order, Courier
from  datetime import datetime

def index(request):
    create_order_form = CreateOrderForm()
    return render(request, 'index.html', {'create_order_form': create_order_form})

def boxes(request):
    return render(request, 'boxes.html')

def faq(request):
    return render(request, 'faq.html')

def my_rent(request):
    return render(request, 'my-rent.html')

def my_rent_empty(request):
    return render(request, 'my-rent-empty.html')


@require_GET
def get_boxes(request):
    try:
        place_id = request.GET.get('place_id')
        boxes_data = []
        if place_id:
            place = Place.objects.get(id=place_id)
            boxes = Box.objects.filter(address=place, is_occupied=False)
            boxes_data = [
                {
                    'id': box.id,
                    'cell_size_price': box.cell_size.price_per_month,
                    'cell_size_name': str(box.cell_size.size),
                    'is_occupied': box.is_occupied,
                    'address_id': box.address.id if box.address else None,
                    'address_name': str(box.address) if box.address else None
                }
                for box in boxes
            ]

        if boxes_data:
            return JsonResponse({'boxes': boxes_data}, status=200)
        else:
            return JsonResponse({'boxes': []}, status=404)

    except Exception as e:
        return  JsonResponse({'error': str(e)}, status=400)


@require_GET
def check_promo(request):
    try:
        promo_name = unquote(request.GET.get('promo_name', ''))

        is_valid = Promo.objects.filter(
            name=promo_name,
            is_active=True
        ).exists()
        if not is_valid:
            return JsonResponse({
                'is_valid': False,
                'error': 'Введите промокод'
            }, status=404)
        return JsonResponse({
            'is_valid': True,
            'promo_name': promo_name
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_POST
@login_required
def create_order(request):
    try:
        user = request.user
        box_id = request.POST.get('cell')
        start_storage = request.POST.get('start_storage')
        end_storage = request.POST.get('end_storage')
        node = request.POST.get('node')
        promo_name = request.POST.get('promo')
        courier_id = request.POST.get('courier')
        box = Box.objects.get(id=box_id)
        start_storage = datetime.strptime(start_storage, '%Y-%m-%d').date()
        end_storage = datetime.strptime(end_storage, '%Y-%m-%d').date()
        price = (end_storage - start_storage).days * box.cell_size.price_per_month

        order = Order(cell=box, start_storage=start_storage, end_storage=end_storage, node=node, cuser=user)
        if promo_name:
            promo = Promo.objects.get(name=promo_name)
            order.promo = promo
            price = price * promo.discount
        if courier_id:
            courier = Courier.objects.get(id=courier_id)
            courier.is_active = True
            courier.save()
            order.courier = courier
        order.total_price = price
        box.is_occupied = True
        box.save()
        order.save()
        return JsonResponse({"create_order":True}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)






