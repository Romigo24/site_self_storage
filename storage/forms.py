from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['start_storage', 'end_storage', 'cell', 'promo', 'node']