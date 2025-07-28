from django.urls import path

from . import views

app_name = 'storage'

urlpatterns = [
    path('', views.index, name='index'),
    path('boxes/', views.boxes, name='boxes'),
    path('faq/', views.faq, name='faq'),
    path('lk/', views.lk, name='lk'),
    path('order/', views.order, name='order'),
    path('my-rent/', views.my_rent, name='my_rent'),
    path('my-rent/empty/', views.my_rent_empty, name='my_rent_empty'),
    path('extend-rent/<int:order_id>/', views.extend_rent, name='extend_rent'),
    path('get_boxes/', views.get_boxes, name='boxes'),
    path('check_promo/',views.check_promo, name='promo'),
    path('create_order/',views.create_order, name='create_order'),

]