from django import forms

from storage.models import Order, Place, Box, Courier


class CreateOrderForm(forms.ModelForm):
    contacts = forms.CharField(required=True, label='Контакты')
    place = forms.ModelChoiceField(queryset=Place.objects.all(), widget=forms.Select(attrs={'class': 'form-control', 'id':'place'}), label='Склад')
    cell = forms.ModelChoiceField(queryset=Box.objects.none(), widget=forms.Select(attrs={'class': 'form-control', 'id':'box'}), label='Бокс')
    start_storage = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}), label='Дата начала аренды')
    end_storage = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}), label='Дата окончания аренды')
    courier = forms.ModelChoiceField(queryset=Courier.objects.filter(is_active=False), widget=forms.Select(attrs={'class': 'form-control', 'id': 'courier'}), required=False, label='Курьер')
    node = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control'}),required=True, label='Список вещей')
    promo = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','id':'promo'}),required=False, label='Промокод')
    class Meta:
        fields = ('place', 'cell', 'start_storage', 'end_storage', 'node', 'contacts', 'courier', 'promo')
        model = Order


