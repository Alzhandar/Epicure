from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse

from .forms import UserRegistrationForm, UserLoginForm
from products.models import Menu
from restaurant.models import Restaurant
from cities.models import City

User = get_user_model()

def home_view(request):
    city_id = request.session.get('city_id')

    restaurants = Restaurant.objects.all()
    if city_id:
        restaurants = restaurants.filter(city_id=city_id)

    cities = City.objects.all().order_by('position', 'name')

    current_city = City.objects.filter(id=city_id).first() if city_id else None
    is_first_visit = not city_id

    menu_items = Menu.objects.filter(is_available=True).select_related('menu_type')

    context = {
        'restaurants': restaurants,
        'cities': cities,
        'current_city': current_city,
        'is_first_visit': is_first_visit,
        'menu_items': menu_items,
    }

    return render(request, 'home.html', context)


def register_view(request):
    if request.user.is_authenticated:
        messages.info(request, 'Вы уже авторизованы.')
        return redirect('home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Аккаунт успешно создан. Добро пожаловать, {user.name}!')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        messages.info(request, 'Вы уже авторизованы.')
        return redirect('home')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = form.user
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.name}!')
            
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)
            
            return redirect('home')
    else:
        form = UserLoginForm()
    
    return render(request, 'users/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('home')

@login_required
def profile_view(request):
    return render(request, 'users/profile.html')

def set_city(request):
    if request.method == 'POST':
        city_id = request.POST.get('city_id')
        if city_id:
            request.session['city_id'] = int(city_id)
            messages.success(request, 'Город успешно выбран')
        
        next_url = request.POST.get('next', 'home')
        return redirect(next_url)
    
    return redirect('home')