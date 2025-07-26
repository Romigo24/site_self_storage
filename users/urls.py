from django.urls import path
from . import views

app_name = 'users'
urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('login/', views.login_view,    name='login'),
    path('logout/', views.logout_view,  name='logout'),
    path('profile/update/', views.profile_update, name='profile_update'),
]