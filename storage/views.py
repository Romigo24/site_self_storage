from django.shortcuts import get_object_or_404, redirect, render
from datetime import timedelta
from django.utils import timezone
from storage.models import Order
from storage.models import Order, Place, Box, BoxTariff
from .forms import OrderForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from .forms import CreateOrderForm
from django.views.decorators.http import  require_GET, require_POST
from urllib.parse import unquote
from django.contrib.auth.decorators import login_required
from .models import Box, Place, Promo, Order, Courier
from  datetime import datetime

def index(request):
    try:
        storage = Place.objects.get(is_show=True)
    except Place.DoesNotExist:
        storage = None
    except Place.MultipleObjectsReturned:
        storage = Place.objects.filter(is_show=True).first()

    create_order_form = CreateOrderForm()

    return render(
        request,
        'index.html',
        {
            'create_order_form': create_order_form,
            'storage': storage,
        }
    )

# def boxes(request):
#     # Получаем все места (склады)
#     places = Place.objects.all().order_by('name')

#     # Получаем все боксы сгруппированные по размеру
#     boxes = Box.objects.select_related('cell_size', 'address').all()

#     # Группируем боксы по размерам для фильтрации
#     boxes_all = boxes
#     boxes_to3 = boxes.filter(cell_size__size__lte=3)
#     boxes_to10 = boxes.filter(cell_size__size__lte=10)
#     boxes_from10 = boxes.filter(cell_size__size__gt=10)

#     context = {
#         'places': places,
#         'boxes_all': boxes_all,
#         'boxes_to3': boxes_to3,
#         'boxes_to10': boxes_to10,
#         'boxes_from10': boxes_from10,
#     }

#     return render(request, 'boxes.html', context)
def boxes(request):
    # Получаем все места (склады)
    places = Place.objects.all().order_by('name')

    # Получаем выбранный склад из параметра запроса
    selected_place_id = request.GET.get('place_id')

    # Если склад выбран, фильтруем боксы по этому складу, иначе показываем все
    if selected_place_id:
        boxes = Box.objects.select_related('cell_size', 'address').filter(address_id=selected_place_id)
    else:
        boxes = Box.objects.select_related('cell_size', 'address').all()

    # Группируем боксы по размерам для фильтрации
    boxes_all = boxes
    boxes_to3 = boxes.filter(cell_size__size__lte=3)
    boxes_to10 = boxes.filter(cell_size__size__lte=10)
    boxes_from10 = boxes.filter(cell_size__size__gt=10)

    context = {
        'places': places,
        'selected_place_id': int(selected_place_id) if selected_place_id else None,
        'boxes_all': boxes_all,
        'boxes_to3': boxes_to3,
        'boxes_to10': boxes_to10,
        'boxes_from10': boxes_from10,
    }

    return render(request, 'boxes.html', context)


def faq(request):
    return render(request, 'faq.html')

@login_required
def my_rent(request):
    user_orders = Order.objects.filter(cuser=request.user)
    active_statuses = ['unprocessed', 'underway', 'delivery']

    active_orders = user_orders.filter(status__in=active_statuses)
    history_orders = user_orders.exclude(status__in=active_statuses)

    has_expiring = active_orders.filter(
        end_storage__lte=timezone.now() + timedelta(days=3)
    ).exists()

    return render(
        request,
        'my-rent.html',
        {
            'active_orders': active_orders,
            'history_orders': history_orders,
            'has_expiring': has_expiring,
        }
    )


@login_required
def extend_rent(request, order_id):
    order = get_object_or_404(Order, id=order_id, cuser=request.user)

    if request.method == 'POST':
        try:
            days = int(request.POST.get('days', '0'))
            if days > 0:
                order.end_storage += timedelta(days=days)
                order.save()
        except (ValueError, TypeError):
            pass

    return redirect('storage:my_rent')


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

@login_required
def lk(request):
    if request.method == 'POST':
        user = request.user
        user.username = request.POST.get('username')
        user.phone = request.POST.get('phone')
        new_password = request.POST.get('password')

        if new_password:
            user.set_password(new_password)
            login(request, user)

        user.save()
        return redirect('storage:lk')

    return render(request, 'lk.html')