from django.shortcuts import get_object_or_404, redirect, render
from datetime import timedelta
from django.utils import timezone
from storage.models import Order
from storage.models import Order, Place, Box, BoxTariff
from .forms import OrderForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login


def index(request):
    try:
        storage = Place.objects.get(is_show=True)
    except Place.DoesNotExist:
        storage = None
    except Place.MultipleObjectsReturned:
        storage = Place.objects.filter(is_show=True).first()

    context = {
        'storage': storage
    }
    return render(request, 'index.html', context)



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


def order(request):
    return render(request, 'order.html')


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


def create_order(request):
    if not request.user.is_authenticated:
        return redirect('users:login')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.cuser = request.user
            order.save()
            return redirect('storage:my_rent')
    else:
        form = OrderForm()

    return render(
        request,
        'order.html',
        {'form': form}
    )