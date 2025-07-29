from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from users.forms import CustomUserCreationForm
from users.models import CustomUser


def register_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('storage:lk')
    else:
        form = CustomUserCreationForm()
    return render(
        request,
        'register.html',
        {'form': form}
    )


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('storage:lk')
        else:
            messages.error(request, 'Неверный логин или пароль')
    else:
        form = AuthenticationForm()

    return render(
        request,
        'login.html',
        {'form': form}
    )


@login_required
def logout_view(request):
    logout(request)
    return redirect('storage:index')


@login_required
def profile_update(request):
    if request.method == 'POST':
        user = request.user
        username = request.POST.get('username')
        phone = request.POST.get('phone')
        password = request.POST.get('password')

        updated_fields = []

        if username and username != user.username:
            user.username = username
            updated_fields.append('E-mail')

        if phone and phone != user.phone:
            user.phone = phone
            updated_fields.append('Телефон')

        if password:
            user.set_password(password)
            update_session_auth_hash(request, user)
            updated_fields.append('Пароль')

        user.save()

        if updated_fields:
            messages.success(request, f"Обновлены: {', '.join(updated_fields)}.")
        else:
            messages.info(request, 'Изменений не было.')

        return redirect('storage:lk')

    return redirect('storage:lk')