from django.shortcuts import get_object_or_404, redirect, render
from datetime import timedelta
from storage.models import Order
from .forms import OrderForm

def index(request):
    return render(request, 'index.html')


def boxes(request):
    return render(request, 'boxes.html')


def faq(request):
    return render(request, 'faq.html')


def my_rent(request):
    if not request.user.is_authenticated:
        return redirect('users:login')

    user_orders = Order.objects.filter(cuser=request.user)

    has_expiring = any(
        order.days_left is not None and order.days_left <= 3
        for order in user_orders
    )

    return render(
        request,
        'my-rent.html',
        {
            'orders': user_orders,
            'has_expiring': has_expiring,
        }
    )


def extend_rent(request, order_id):
    if not request.user.is_authenticated:
        return redirect('users:login')

    order = get_object_or_404(Order, id=order_id, cuser=request.user)

    order.end_storage += timedelta(days=7)
    order.save()
    return redirect('storage:my_rent')


def my_rent_empty(request):
    return render(request, 'my-rent-empty.html')


def order(request):
    return render(request, 'order.html')


def lk(request):
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